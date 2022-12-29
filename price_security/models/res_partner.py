from odoo import models, api
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_only_view'):
                readonly_fields = (arch.xpath("//field[@name='property_product_pricelist']")
                                    + arch.xpath("//field[@name='property_payment_term_id']"))
                for node in readonly_fields:
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in arch.xpath("//group[@name='sale']/div/button[@name='action_company_properties']"):
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view
