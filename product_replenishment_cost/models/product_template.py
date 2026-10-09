##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
import random
import time

from odoo import _, api, fields, models
from odoo.service.model import MAX_TRIES_ON_CONCURRENCY_FAILURE, PG_CONCURRENCY_EXCEPTIONS_TO_RETRY
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    supplier_currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_supplier_data",
        compute_sudo=True,
    )
    supplier_price = fields.Float(
        compute="_compute_supplier_data",
        compute_sudo=True,
        digits="Product Price",
    )
    supplier_uom_id = fields.Many2one(
        "uom.uom",
        compute="_compute_supplier_data",
        compute_sudo=True,
    )
    standard_price = fields.Float(
        string="Accounting Cost",
    )
    replenishment_cost = fields.Float(
        compute="_compute_replenishment_cost",
        compute_sudo=True,
        # TODO, activamos store como estaba??
        store=False,
        digits="Product Price",
        help="Replenishment cost on the currency of the product",
    )
    replenishment_cost_last_update = fields.Datetime(
        # no tracking: the compute fires on every rule change, one chatter message per product
        compute="_compute_replenishment_cost_last_update",
        store=True,
        help="Date of the last update of replenishment base cost or its currency",
    )
    replenishment_base_cost = fields.Float(
        digits="Product Price",
        tracking=True,
        help="Replanishment Cost expressed in 'Replenishment Base Cost Currency'.",
    )
    replenishment_base_cost_currency_id = fields.Many2one(
        "res.currency",
        "Replenishment Base Cost Currency",
        bypass_search_access=True,
        tracking=True,
        help="Currency used for the Replanishment Base Cost.",
        default=lambda self: self.env.company.currency_id.id,
    )
    replenishment_cost_rule_id = fields.Many2one(
        "product.replenishment_cost.rule",
        bypass_search_access=True,
        index=True,
        tracking=True,
        help="Rule of surcharges and discounts applied on the base cost to compute the " "final replenishment cost.",
    )
    replenishment_base_cost_on_currency = fields.Float(
        compute="_compute_replenishment_cost",
        compute_sudo=True,
        help="Replenishment cost on replenishment base cost currency",
        digits="Product Price",
    )
    replenishment_cost_type = fields.Selection(
        [
            ("supplier_price", "Main Supplier Price"),
            ("last_supplier_price", "Last Supplier Price"),
            ("manual", "Manual"),
        ],
        default="manual",
        required=True,
        help="Source of the replenishment cost: the main supplier's price, the last "
        "recorded supplier price, or a value entered manually.",
    )

    warnings_cost = fields.Json(compute="_compute_warnings_cost")

    @api.depends_context("company")
    @api.depends(
        "seller_ids.net_price",
        "seller_ids.currency_id",
        "seller_ids.product_uom_id",
        "seller_ids.company_id",
        "replenishment_cost_type",
    )
    def _compute_supplier_data(self):
        """Lo ideal seria utilizar campo related para que segun los permisos
         del usuario tome el seller_id que corresponda, pero el tema es que el
         cron se corre con admin y entonces siempre va a tomar el primer seller
        sin importar si estamos usando un force_company para poder definir rel
         costo en distintas compañias.
        Basicamente usamos regla analoga a la que viene por defecto para los
         sellers donde se puede ver si
        no tiene cia o es cia del usuario.
        """
        company_id = self.env.company.id
        for rec in self:
            seller_ids = rec.seller_ids.filtered(lambda x: not x.company_id or x.company_id.id == company_id)
            if rec.replenishment_cost_type == "last_supplier_price":
                seller_ids = seller_ids.sorted(key="last_date_price_updated", reverse=True)
            rec.update(
                {
                    "supplier_price": seller_ids and seller_ids[0].net_price or 0.0,
                    "supplier_currency_id": seller_ids and seller_ids[0].currency_id or self.env["res.currency"],
                    "supplier_uom_id": seller_ids and seller_ids[0].product_uom_id or self.env["uom.uom"],
                }
            )

    @api.model
    def cron_update_cost_from_replenishment_cost(self, limit=None, company_ids=None, batch_size=1000):
        """Retry the batch on PostgreSQL concurrency errors: crons do not retry like HTTP does."""
        for attempt in range(1, MAX_TRIES_ON_CONCURRENCY_FAILURE + 1):
            try:
                return self._cron_update_cost_from_replenishment_cost(
                    limit=limit, company_ids=company_ids, batch_size=batch_size
                )
            except PG_CONCURRENCY_EXCEPTIONS_TO_RETRY as exc:
                # the transaction is aborted: rollback and reset the cache before retrying, as core does
                self.env.cr.rollback()
                self.env.transaction.reset()
                if attempt == MAX_TRIES_ON_CONCURRENCY_FAILURE:
                    _logger.error(
                        "cron_update_cost_from_replenishment_cost: error de concurrencia (%s) "
                        "tras %s intentos, se aborta y el job queda fallido.",
                        exc.__class__.__name__,
                        MAX_TRIES_ON_CONCURRENCY_FAILURE,
                    )
                    self._mark_running_run_as_error(exc, company_ids=company_ids)
                    raise
                wait_time = random.uniform(0.0, 2**attempt)
                _logger.warning(
                    "cron_update_cost_from_replenishment_cost: error de concurrencia (%s), "
                    "intento %s/%s, reintentando en %.2fs",
                    exc.__class__.__name__,
                    attempt,
                    MAX_TRIES_ON_CONCURRENCY_FAILURE,
                    wait_time,
                )
                time.sleep(wait_time)
            except Exception as exc:
                # any other error leaves the job failed, visible from the interface
                self._mark_running_run_as_error(exc, company_ids=company_ids)
                raise

    @api.model
    def _mark_running_run_as_error(self, exc, company_ids=None):
        """Log the cron failure on a separate cursor, so it survives the rollback and the re-raise."""
        self.env.cr.rollback()
        self.env.transaction.reset()
        with self.pool.cursor() as cr:
            self.env(cr=cr)["product.replenishment_cost.run"]._log_cron_failure(
                "%s: %s" % (exc.__class__.__name__, exc), company_ids=company_ids
            )
        return True

    @api.model
    def _cron_update_cost_from_replenishment_cost(self, limit=None, company_ids=None, batch_size=1000):
        """Update accounting cost in batches, chaining the cron until the catalogue is done.

        Every chained batch shares one ``product.replenishment_cost.run``.
        """
        if not company_ids:
            company_ids = self.env["res.company"].search([]).ids

        run = self.env["product.replenishment_cost.run"]._get_or_create_cron_run(company_ids=company_ids)

        # one extra record tells us whether work remains, without walking the whole table
        records = self.with_context(prefetch_fields=False).search(
            [("id", ">", run.cursor_template_id)], order="id asc", limit=batch_size + 1
        )
        batch = records[:batch_size]
        pending = len(records) > batch_size

        for company_id in company_ids:
            _logger.info("Running cron update cost from replenishment for company %s", company_id)
            batch.with_company(company=company_id).with_context(
                bypass_base_automation=True
            )._update_cost_from_replenishment_cost(run=run)

        run._add_counters({"template_count": len(batch)})
        run.sudo().write(
            {
                "cursor_template_id": batch[-1].id if (pending and batch) else 0,
                "batch_count": run.batch_count + 1,
            }
        )
        if not pending:
            run._finish()
        # Uso directo de cr.commit(). Buscar alternativa menos riesgosa
        self.env.cr.commit()  # pragma pylint: disable=invalid-commit

        # chain the cron for the next batch
        if pending:
            # para obtener el job_id se requiere este PR https://github.com/odoo/odoo/pull/146147
            cron = self.env["ir.cron"].browse(self.env.context.get("job_id")) or self.env.ref(
                "product_replenishment_cost.ir_cron_update_cost_from_replenishment_cost"
            )
            cron._trigger()
        return run

    def _update_cost_from_replenishment_cost(self, run=None):
        """
        If we came from tree list, we update only in selected list
        Actulizamos product.product ya que el standard_price esta en ese modelo

        Counters and one line per changed cost are logged on ``run`` when given.
        """
        prec = self.env["decimal.precision"].precision_get("Product Price")

        # clave hacerlo en product.product por velocidad (relativo a
        # campos standard_price)
        company = self.env.company
        products = (
            self.with_context(tracking_disable=True)
            .env["product.product"]
            .search([("product_tmpl_id.id", "in", self.ids)])
        )
        counters = {"template_count": len(self), "evaluated_count": 0, "updated_count": 0, "unchanged_count": 0}
        line_vals = []
        for product in products.filtered("replenishment_cost"):
            counters["evaluated_count"] += 1
            replenishment_cost = product.replenishment_cost
            if product.currency_id != product.cost_currency_id:
                replenishment_cost = product.currency_id._convert(
                    replenishment_cost,
                    product.cost_currency_id,
                    product.company_id or company,
                    fields.Date.today(),
                    round=True,
                )
            if float_compare(product.standard_price, replenishment_cost, precision_digits=prec) != 0:
                previous_cost = product.standard_price
                product.standard_price = replenishment_cost
                counters["updated_count"] += 1
                if run:
                    line_vals.append(
                        {
                            "run_id": run.id,
                            "product_id": product.id,
                            "company_id": company.id,
                            "currency_id": product.cost_currency_id.id,
                            "previous_cost": previous_cost,
                            "new_cost": replenishment_cost,
                        }
                    )
            else:
                counters["unchanged_count"] += 1
        if run:
            if line_vals:
                self.env["product.replenishment_cost.run.line"].sudo().create(line_vals)
            # templates are counted by the caller: the cron walks the same batch once per company
            run._add_counters({name: value for name, value in counters.items() if name != "template_count"})
        return counters

    @api.depends(
        "replenishment_cost_type",
        "replenishment_base_cost",
        "replenishment_base_cost_currency_id",
        "supplier_price",
        "supplier_currency_id",
        "replenishment_cost_rule_id.item_ids.sequence",
        "replenishment_cost_rule_id.item_ids.percentage_amount",
        "replenishment_cost_rule_id.item_ids.fixed_amount",
    )
    def _compute_replenishment_cost_last_update(self):
        self.replenishment_cost_last_update = fields.Datetime.now()

    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        "currency_id",
        "supplier_price",
        "supplier_currency_id",
        "supplier_uom_id",
        "uom_id",
        "replenishment_cost_type",
        "replenishment_base_cost",
        "replenishment_base_cost_currency_id",
        "replenishment_cost_rule_id",
    )
    @api.depends_context("company")
    def _compute_replenishment_cost(self):
        _logger.debug("Getting replenishment cost for %s products", len(self.ids))
        company = self.env.company
        date = fields.Date.today()
        for rec in self:
            product_currency = rec.currency_id
            rec.replenishment_base_cost_on_currency = 0.0
            rec.replenishment_cost = 0.0
            base_cost_currency = False
            if rec.replenishment_cost_type in ["supplier_price", "last_supplier_price"]:
                # supplier price is in the supplier UoM, rules apply on the product UoM
                replenishment_base_cost = rec.supplier_price
                if rec.supplier_uom_id and rec.uom_id:
                    replenishment_base_cost = rec.supplier_uom_id._compute_price(replenishment_base_cost, rec.uom_id)
                base_cost_currency = rec.supplier_currency_id
            elif rec.replenishment_cost_type == "manual":
                replenishment_base_cost = rec.replenishment_base_cost
                base_cost_currency = rec.replenishment_base_cost_currency_id

            # we enforce a replenishment base cost currency to be configured
            if not base_cost_currency:
                continue

            replenishment_cost_rule = rec.replenishment_cost_rule_id
            replenishment_cost = base_cost_currency._convert(
                replenishment_base_cost, product_currency, company, date, round=False
            )

            replenishment_base_cost_on_currency = replenishment_cost
            if replenishment_cost_rule:
                replenishment_cost = replenishment_cost_rule.compute_rule(replenishment_base_cost_on_currency, rec)

            rec.update(
                {
                    "replenishment_base_cost_on_currency": replenishment_base_cost_on_currency,
                    "replenishment_cost": replenishment_cost,
                }
            )

    def _compute_warnings_cost(self):
        warnings = {}
        if self.env["res.company"].sudo().search_count([]) > 1:
            warnings["company_info"] = {
                "message": _("Replenishment cost based on company: %s.", self.env.company.name),
                "action_text": False,
                "action": False,
                "level": "info",
            }

        self.warnings_cost = warnings
