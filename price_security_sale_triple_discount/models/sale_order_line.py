##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _price_security_settle_discount(self, vals_list):
        # sale_triple_discount rewires discount as a compute over discount1/2/3, whose
        # circular compute/inverse chain leaves the pricelist discount unsettled during
        # the create flush: lines created without an explicit discount (e.g. adding
        # products from the catalog view) transiently read 0.0 and were wrongly
        # rejected by the discount restriction check. Re-marking the fields to compute
        # makes the next read (the restriction check) resolve the settled values.
        super()._price_security_settle_discount(vals_list)
        discount_fields = {"discount", "discount1", "discount2", "discount3"}
        to_settle = self.browse(line.id for line, vals in zip(self, vals_list) if not discount_fields & vals.keys())
        amount_fields = ("price_subtotal", "price_total", "price_reduce_taxexcl", "price_reduce_taxinc")
        for fname in to_settle and ("discount1", "discount2", "discount3", "discount") + amount_fields or ():
            self.env.add_to_compute(self._fields[fname], to_settle)
