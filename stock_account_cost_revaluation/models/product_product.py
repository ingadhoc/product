##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo import Command, _, models
from odoo.tools import float_compare, float_is_zero

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _change_standard_price(self, old_price):
        """En v19 cambiar ``standard_price`` ya no genera el asiento de revaluación
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
        res = super()._change_standard_price(old_price)
        for product in self:
            if product not in old_price:
                continue
            product._create_cost_revaluation_entry(old_price[product])
        return res

    def _create_cost_revaluation_entry(self, old_price):
        """Contabiliza la diferencia de valuación de inventario por el cambio de
        ``standard_price`` (costo nuevo vs. previo) sobre el stock on hand.

        Solo aplica a productos con categoría de valoración perpetua
        (``real_time``) y costeo **estándar o promedio (AVCO)**: en ambos el cambio
        de ``standard_price`` revalúa el stock on hand (en AVCO el core lo usa como
        ancla de revaluación, ver ``_run_average_batch``). **FIFO queda excluido**:
        ahí ``standard_price`` es informativo y el core ni siquiera registra el
        ``product.value`` — su revaluación se hace ajustando el valor del
        movimiento/capa, que es otro mecanismo.

        La contrapartida es la **cuenta de revaluación de inventario** configurada
        en la categoría (``property_cost_revaluation_account_id``), que es la cuenta
        de resultado de la revaluación. Igual que el core con el
        ``valuation_account_id`` de una ubicación de scrap/ajuste: si no está
        configurada, **no se postea** el asiento. El signo lo maneja
        ``res.company._prepare_inventory_aml_vals``.
        """
        self.ensure_one()
        company = self.env.company

        # ``valuation`` se resuelve desde categ_id.property_valuation (con fallback
        # a la compañía); gateamos en real_time para excluir las periódicas.
        if self.valuation != "real_time" or self.cost_method not in ("standard", "average"):
            return self.env["account.move"]
        if not self.is_storable:
            return self.env["account.move"]

        prec = self.env["decimal.precision"].precision_get("Product Price")
        new_price = self.standard_price
        if float_compare(new_price, old_price, precision_digits=prec) == 0:
            return self.env["account.move"]

        # cantidad valorizada on hand (en la compañía actual)
        quantity = self.qty_available
        if float_is_zero(quantity, precision_rounding=self.uom_id.rounding):
            return self.env["account.move"]

        # delta > 0 (sube el costo) => aumenta el activo de inventario
        delta_value = company.currency_id.round(quantity * (new_price - old_price))
        if company.currency_id.is_zero(delta_value):
            return self.env["account.move"]

        accounts = self.product_tmpl_id.get_product_accounts()
        valuation_account = accounts.get("stock_valuation")
        journal = accounts.get("stock_journal")
        # Contrapartida = cuenta de revaluación de inventario configurada en la
        # categoría (cuenta de resultado). Misma lógica que el core con la cuenta de
        # una ubicación de scrap/ajuste: si no está configurada, no se postea.
        counterpart_account = self.categ_id.property_cost_revaluation_account_id
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
        line_vals = company._prepare_inventory_aml_vals(
            valuation_account, counterpart_account, delta_value, ref, product_id=self.id
        )

        move = (
            self.env["account.move"]
            .sudo()
            .create(
                {
                    "journal_id": journal.id,
                    "company_id": company.id,
                    "ref": ref,
                    "move_type": "entry",
                    "line_ids": [Command.create(vals) for vals in line_vals],
                }
            )
        )
        move._post()
        return move
