##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
# flake8: noqa
# pylint: disable=pointless-string-statement
from odoo import api
from odoo.addons.product.models.product import ProductProduct

# NOTE This is a exact copy of an odoo method, here we change a part of the
# code directly since the original code is not inheritable possible.
@api.multi
def new_name_get(self):
    # TDE: this could be cleaned a bit I think

    def _name_get(d):
        name = d.get('name', '')
        code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
        if code:
            name = '[%s] %s' % (code,name)
        return (d['id'], name)

    partner_id = self._context.get('partner_id')
    if partner_id:
        partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
    else:
        partner_ids = []

    # all user don't have access to seller and partner
    # check access and use superuser
    self.check_access_rights("read")
    self.check_access_rule("read")

    result = []

    # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
    # Use `load=False` to not call `name_get` for the `product_tmpl_id`
    self.sudo().read(['name', 'default_code', 'product_tmpl_id', 'attribute_value_ids', 'attribute_line_ids'], load=False)

    product_template_ids = self.sudo().mapped('product_tmpl_id').ids

    if partner_ids:
        supplier_info = self.env['product.supplierinfo'].sudo().search([
            ('product_tmpl_id', 'in', product_template_ids),
            ('name', 'in', partner_ids),
        ])
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
        supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
        supplier_info_by_template = {}
        for r in supplier_info:
            supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
    for product in self.sudo():
        # display only the attributes with multiple possible values on the template
        # THIS IS THE ORIGINAL CODE WE WANT TO REPLACE
        """
        variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
        """
        # THIS IS THE START OF OUR CHANGES
        variable_attributes = product.attribute_line_ids.filtered(lambda l: l.attribute_id.add_to_name or len(l.value_ids) > 1).mapped('attribute_id')
        # THIS IS THE END OF OUR CHANGES
        variant = product.attribute_value_ids._variant_name(variable_attributes)
        name = variant and "%s (%s)" % (product.name, variant) or product.name
        sellers = []
        if partner_ids:
            product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
            sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
            if not sellers:
                sellers = [x for x in product_supplier_info if not x.product_id]
        if sellers:
            for s in sellers:
                seller_variant = s.product_name and (
                    variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                mydict = {
                            'id': product.id,
                            'name': seller_variant or name,
                            'default_code': s.product_code or product.default_code,
                            }
                temp = _name_get(mydict)
                if temp not in result:
                    result.append(temp)
        else:
            mydict = {
                        'id': product.id,
                        'name': name,
                        'default_code': product.default_code,
                        }
            result.append(_name_get(mydict))
    return result

ProductProduct.name_get = new_name_get
