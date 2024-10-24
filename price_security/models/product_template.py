##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api
import json


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_modify_prices = fields.Boolean(
        help="If checked all users can modify the "
        "price of this product in a sale order or invoice.",
        string='Can modify prices')

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        """The override of fields_get making fields readonly for price security users
        makes the view cache dependent on the fact the user has the group price security or not
        """
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (self.env.user.has_group('price_security.group_only_view'),) + \
            (self.env.user.has_group('price_security.group_only_view_sale_price'),)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            if self.env.user.has_group('price_security.group_only_view'):
                readonly_fields = (arch.xpath("//field[@name='can_modify_prices']")
                                    + arch.xpath("//field[@name='list_price']")
                                    + arch.xpath("//field[@name='uom_id']")
                                    + arch.xpath("//field[@name='seller_ids']")
                                    + arch.xpath("//field[@name='variant_seller_ids']")
                                    + arch.xpath("//field[@name='uom_po_id']")
                                    + arch.xpath("//field[@name='standard_price']"))
                for node in readonly_fields:
                    node.set('readonly', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.env.user.has_group('price_security.group_only_view_sale_price'):
                invisible_fields = (arch.xpath("//div[@name='standard_price_uom']")
                                    + arch.xpath("//field[@name='seller_ids']")
                                    + arch.xpath("//field[@name='variant_seller_ids']")
                                    + arch.xpath("//field[@name='uom_po_id']")
                                    + arch.xpath("//label[@for='standard_price']")
                                    + arch.xpath("//field[@name='standard_price']"))
                for node in invisible_fields:
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if view_type == 'list':
            if self.env.user.has_group('price_security.group_only_view_sale_price'):
                for node in arch.xpath("//field[@name='standard_price']"):
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        return arch, view

