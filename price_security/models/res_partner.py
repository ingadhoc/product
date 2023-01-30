from odoo import api, models
from lxml import etree
import json

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        If we came from sale order, we send in context 'force_product_edit'
        and we change tree view to make editable and also field qty
        """
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_restrict_prices'):
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//group[@name='sale']/div/button[@name='action_company_properties']"):
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
        return res
