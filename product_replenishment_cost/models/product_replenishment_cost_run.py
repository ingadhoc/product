##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools.mail import plaintext2html

_logger = logging.getLogger(__name__)

# Parámetros de sistema que gobiernan el registro de corridas
LINE_RETENTION_PARAM = "product_replenishment_cost.run_line_retention_days"
DEFAULT_LINE_RETENTION_DAYS = 90
# Una corrida encadena batches sin pausas; si hace horas que no escribe es que murió
STALE_RUN_HOURS = 6
# Tope de borrado por corrida del cron de purga, para no hacer una transacción eterna
PURGE_BATCH_SIZE = 5000
PURGE_MAX_LINES = 100000
# Cursor viejo, previo al registro de corridas. Se lee una vez para no reprocesar.
LEGACY_CURSOR_PARAM = "product_replenishment_cost.last_updated_record_id"


class ProductReplenishmentCostRun(models.Model):
    _name = "product.replenishment_cost.run"
    _description = "Replenishment Cost Update Run"
    _inherit = ["mail.thread"]
    _order = "date_start desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    date_start = fields.Datetime(required=True, readonly=True, default=fields.Datetime.now)
    date_end = fields.Datetime(readonly=True)
    duration = fields.Float(
        "Duration (min)",
        compute="_compute_duration",
        store=True,
        help="Minutes between the start and the end of the run.",
    )
    trigger = fields.Selection(
        [
            ("cron", "Scheduled Action"),
            ("wizard", "Manual Update"),
            ("manual", "Manual"),
        ],
        required=True,
        default="manual",
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        "Launched by",
        readonly=True,
        default=lambda self: self.env.user,
    )
    company_ids = fields.Many2many("res.company", string="Companies", readonly=True)
    state = fields.Selection(
        [
            ("running", "Running"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        default="running",
        required=True,
        readonly=True,
        tracking=True,
    )
    error_message = fields.Text(readonly=True)
    batch_count = fields.Integer(readonly=True)
    template_count = fields.Integer("Products Processed", readonly=True)
    evaluated_count = fields.Integer("Variants Evaluated", readonly=True)
    updated_count = fields.Integer("Costs Updated", readonly=True)
    unchanged_count = fields.Integer("Without Changes", readonly=True)
    cursor_template_id = fields.Integer(
        "Cursor",
        readonly=True,
        help="Id of the last product template processed. Zero means the run went through all of them.",
    )
    line_ids = fields.One2many(
        "product.replenishment_cost.run.line",
        "run_id",
        "Updated Costs",
        readonly=True,
    )

    @api.depends("date_start", "trigger")
    def _compute_name(self):
        triggers = dict(self.fields_get(["trigger"])["trigger"]["selection"])
        for rec in self:
            date_start = fields.Datetime.context_timestamp(rec, rec.date_start) if rec.date_start else False
            rec.name = "%s - %s" % (
                date_start and date_start.strftime("%Y-%m-%d %H:%M") or self.env._("New"),
                triggers.get(rec.trigger, ""),
            )

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                rec.duration = (rec.date_end - rec.date_start).total_seconds() / 60.0
            else:
                rec.duration = 0.0

    @api.model
    def _get_or_create_cron_run(self, company_ids=None):
        """Devuelve la corrida en curso del cron o crea una nueva.

        Una pasada completa del cron son varios batches encadenados: todos comparten
        la misma corrida para que "cuándo terminó" tenga sentido. Si la corrida
        anterior quedó abierta es que el proceso murió: la cerramos como error
        (así se ve desde la interfaz) y arrancamos otra desde su mismo cursor.
        """
        run = self.sudo().search([("state", "=", "running"), ("trigger", "=", "cron")], limit=1)
        if run:
            stale_before = fields.Datetime.now() - relativedelta(hours=STALE_RUN_HOURS)
            if run.write_date > stale_before:
                return run
            cursor = run.cursor_template_id
            run._finish(
                state="error",
                error_message=self.env._(
                    "The run was interrupted: it did not report progress for more than %s hours.", STALE_RUN_HOURS
                ),
            )
            return self._create_run(trigger="cron", company_ids=company_ids, cursor_template_id=cursor)
        return self._create_run(trigger="cron", company_ids=company_ids)

    @api.model
    def _create_run(self, trigger="manual", company_ids=None, cursor_template_id=None):
        if cursor_template_id is None:
            cursor_template_id = self._pop_legacy_cursor()
        return (
            self.sudo()
            .create(
                {
                    "trigger": trigger,
                    "company_ids": [(6, 0, company_ids or [self.env.company.id])],
                    "cursor_template_id": cursor_template_id,
                    "user_id": self.env.user.id,
                }
            )
            .with_env(self.env)
        )

    @api.model
    def _pop_legacy_cursor(self):
        """Toma el cursor que quedó en ir.config_parameter antes de esta funcionalidad."""
        param = self.env["ir.config_parameter"].sudo().search([("key", "=", LEGACY_CURSOR_PARAM)], limit=1)
        if not param:
            return 0
        cursor = int(param.value or 0)
        if cursor:
            param.value = "0"
        return cursor

    def _add_counters(self, counters):
        self.ensure_one()
        self.sudo().write(
            {
                "template_count": self.template_count + counters.get("template_count", 0),
                "evaluated_count": self.evaluated_count + counters.get("evaluated_count", 0),
                "updated_count": self.updated_count + counters.get("updated_count", 0),
                "unchanged_count": self.unchanged_count + counters.get("unchanged_count", 0),
            }
        )

    def _finish(self, state="done", error_message=False):
        self.ensure_one()
        self.sudo().write(
            {
                "state": state,
                "date_end": fields.Datetime.now(),
                "error_message": error_message,
            }
        )
        self._post_summary()
        return True

    def _get_summary(self):
        self.ensure_one()
        return self.env._(
            "Replenishment cost update finished.\n"
            "Products processed: %(templates)s\n"
            "Costs updated: %(updated)s\n"
            "Without changes: %(unchanged)s\n"
            "Companies: %(companies)s",
            templates=self.template_count,
            updated=self.updated_count,
            unchanged=self.unchanged_count,
            companies=", ".join(self.company_ids.mapped("name")) or "-",
        )

    def _post_summary(self):
        for rec in self:
            body = rec._get_summary()
            if rec.state == "error":
                body = self.env._("The replenishment cost update failed: %s", rec.error_message or "")
            rec.sudo().message_post(body=plaintext2html(body), subtype_xmlid="mail.mt_note")

    def action_view_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Updated Costs"),
            "res_model": "product.replenishment_cost.run.line",
            "view_mode": "list",
            "domain": [("run_id", "=", self.id)],
            "context": {"create": False},
        }

    @api.model
    def _cron_purge_run_lines(self):
        """Borra el detalle viejo de las corridas. La cabecera queda (es liviana).

        Se borra de a lotes con commit intermedio: la primera purga de una base con
        historial puede ser grande y no queremos una transacción larga.
        """
        days = int(self.env["ir.config_parameter"].sudo().get_param(LINE_RETENTION_PARAM, DEFAULT_LINE_RETENTION_DAYS))
        if days <= 0:
            return True
        limit_date = fields.Datetime.now() - relativedelta(days=days)
        Line = self.env["product.replenishment_cost.run.line"].sudo()
        purged = 0
        while purged < PURGE_MAX_LINES:
            lines = Line.search([("create_date", "<", limit_date)], limit=PURGE_BATCH_SIZE)
            if not lines:
                break
            purged += len(lines)
            lines.unlink()
            self.env.cr.commit()  # pragma pylint: disable=invalid-commit
        if purged:
            _logger.info("Purged %s replenishment cost run lines older than %s days", purged, days)
        return True


class ProductReplenishmentCostRunLine(models.Model):
    _name = "product.replenishment_cost.run.line"
    _description = "Replenishment Cost Update Run Line"
    _order = "id desc"

    run_id = fields.Many2one(
        "product.replenishment_cost.run",
        "Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    date = fields.Datetime(related="run_id.date_start", store=True)
    product_id = fields.Many2one(
        "product.product",
        "Product",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one("res.company", "Company", required=True)
    currency_id = fields.Many2one("res.currency", "Currency")
    previous_cost = fields.Float(digits="Product Price")
    new_cost = fields.Float(digits="Product Price")
