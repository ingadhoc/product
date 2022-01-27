##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import api, models, tools, exceptions, _


class IrModelAccess(models.Model):

    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self.env.uid', 'self.env.su', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):

        if isinstance(model, models.BaseModel):
            assert model._name == 'ir.model', 'Invalid model object'
            model_name = model.model
        else:
            model_name = model
        # we need to use this flag to know when the operation is from this modules
        if self._context.get('sale_quotation_products') or self._context.get('purchase_quotation_products') or self.env.is_superuser():
            return True

        if mode != 'read' and model_name in [
                'product.template', 'product.product']:
            if self.env['res.users'].has_group(
                    'product_management_group.group_products_management'):
                return True
            elif raise_exception:
                raise exceptions.AccessError(_(
                    "Sorry, you are not allowed to manage products."
                    "Only users with 'Products Management' level are currently"
                    " allowed to do that"))
            else:
                return False
        return super(IrModelAccess, self).check(
            model, mode=mode, raise_exception=raise_exception)
