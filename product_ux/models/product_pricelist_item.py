from odoo import models, fields, api

class PicelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    applied_description = fields.Char(compute="_compute_applied_description")

    @api.depends('applied_on', 'product_tmpl_id', 'product_id', 'categ_id')
    def _compute_applied_description(self):
        for rec in self:
            if rec.applied_on == '0_product_variant':
                rec.applied_description = rec.product_id.display_name
            elif rec.applied_on == '1_product':
                rec.applied_description = rec.product_tmpl_id.display_name
            elif rec.applied_on == '2_product_category':
                rec.applied_description = rec.categ_id.display_name
            else:
                rec.applied_description = False

