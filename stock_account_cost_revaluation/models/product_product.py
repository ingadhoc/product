##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo import Command, _, fields, models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _change_standard_price(self, old_price, valuation_date=None):
        """Desde v19 cambiar ``standard_price`` ya no genera el asiento de revaluación
        de inventario: el core solo registra un ``product.value`` (línea de tiempo
        del costo) y delega el impacto contable al cierre de inventario
        (``action_close_stock_valuation``).

        El problema es que el cron de cierre (``_cron_post_stock_valuation``)
        **excluye explícitamente** las compañías con valoración perpetua
        (``real_time``), por lo que para esos productos la revaluación por un
        cambio de costo nunca se materializa sola.

        Acá cubrimos ese hueco: tras el comportamiento estándar, posteamos el
        asiento de revaluación para los productos cuya **categoría tiene valoración
        ``real_time``**. Como es el chokepoint de todo cambio de ``standard_price``,
        aplica a cualquier origen del ajuste (edición manual del costo contable,
        cron de costo de reposición, importaciones, etc.).
        """
        ProductValue = self.env["product.value"].sudo()
        last_id = ProductValue.search([], order="id desc", limit=1).id or 0
        res = super()._change_standard_price(old_price, valuation_date=valuation_date)
        # the price changes the standard just recorded, one per product (lots aside)
        new_values = ProductValue.search(
            [("id", ">", last_id), ("product_id", "in", self.ids), ("move_id", "=", False), ("lot_id", "=", False)]
        )
        values_by_product_id = {pv.product_id.id: pv for pv in new_values}
        for product in self:
            product_value = values_by_product_id.get(product.id)
            if product_value:
                product._create_cost_revaluation_entry(product_value)
        return res

    def _create_cost_revaluation_entry(self, product_value):
        """Contabiliza la diferencia de valuación de inventario por el cambio de
        ``standard_price`` (costo nuevo vs. previo) sobre el stock on hand.

        Solo aplica a productos con categoría de valoración perpetua
        (``real_time``) y costeo **estándar o promedio (AVCO)**: en ambos el cambio
        de ``standard_price`` revalúa el stock on hand (en AVCO el core lo usa como
        ancla de revaluación, ver ``_run_average_batch``). **FIFO queda excluido**:
        ahí ``standard_price`` es informativo y el core ni siquiera registra el
        ``product.value`` — su revaluación se hace ajustando el valor del
        movimiento/capa, que es otro mecanismo.

        Cantidad, ajuste, compañía y fecha salen del ``product.value`` que el core
        registró por este cambio, y el asiento queda apuntado ahí
        (``account_move_id``) para que no se contabilice dos veces.

        La contrapartida es la **cuenta de revaluación de inventario** configurada
        en la categoría (``property_cost_revaluation_account_id``), que es la cuenta
        de resultado de la revaluación. Igual que el core con el
        ``valuation_account_id`` de una ubicación de scrap/ajuste: si no está
        configurada, **no se postea** el asiento. El signo lo maneja
        ``res.company._prepare_inventory_aml_vals``.
        """
        self.ensure_one()
        company = product_value.company_id
        product = self.with_company(company)

        # ``valuation`` se resuelve desde categ_id.property_valuation (con fallback
        # a la compañía); gateamos en real_time para excluir las periódicas.
        if product.valuation != "real_time" or product.cost_method not in ("standard", "average"):
            return self.env["account.move"]
        if self.uom_id.is_zero(product_value.quantity):
            return self.env["account.move"]

        # delta > 0 (sube el costo) => aumenta el activo de inventario
        delta_value = company.currency_id.round(product_value.adjustment)
        if company.currency_id.is_zero(delta_value):
            return self.env["account.move"]

        accounts = product.product_tmpl_id.get_product_accounts()
        valuation_account = accounts.get("stock_valuation")
        journal = accounts.get("stock_journal")
        # Contrapartida = cuenta de revaluación de inventario configurada en la
        # categoría (cuenta de resultado). Misma lógica que el core con la cuenta de
        # una ubicación de scrap/ajuste: si no está configurada, no se postea.
        counterpart_account = product.categ_id.property_cost_revaluation_account_id
        if not counterpart_account:
            return self.env["account.move"]
        if not (valuation_account and journal):
            _logger.warning(
                "No se pudo contabilizar la revaluación del producto %s: falta la cuenta de "
                "valuación o el diario de stock.",
                self.display_name,
            )
            return self.env["account.move"]

        ref = _("Revaluación de costo: %s", self.display_name)
        # Debe cuenta de valuación / Haber cuenta de revaluación (el signo
        # según el delta lo maneja _prepare_inventory_aml_vals).
        line_vals = company._prepare_inventory_aml_vals(valuation_account, counterpart_account, delta_value, ref)
        move = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "journal_id": journal.id,
                    "company_id": company.id,
                    "ref": ref,
                    "move_type": "entry",
                    "date": fields.Date.context_today(self, timestamp=product_value.date),
                    "line_ids": [Command.create({**vals, "product_id": self.id}) for vals in line_vals],
                }
            )
        )
        move._post()
        product_value.account_move_id = move
        return move
