##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import _, api, exceptions, models

ACCESS_ERROR_MSG = "Sorry, you are not allowed to manage products. Only users with 'Products Management' level are currently allowed to do that"


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    @api.model
    def check(self, model, mode="read", raise_exception=True):
        # permitimos que si se llama con super user no haya restriccion por mas que no este en el grupo
        # esto, entre otras cosas, resuelve un error al ir a ver producto en ecommerce y tmb el caso
        # donde hay acciones automaticas sobre modelo product.product y se usa sale_quotation_products

        if self.env.is_superuser():
            return True

        if self._raise_condition(model, mode):
            if self.env.user.has_group("product_management_group.group_products_management"):
                return True
            elif raise_exception:
                raise exceptions.AccessError(_(ACCESS_ERROR_MSG))
            else:
                return False
        return super(IrModelAccess, self).check(model, mode=mode, raise_exception=raise_exception)

    def _make_access_error(self, model: str, mode: str):
        # Agregamos este método porque hay casos donde la función check se llama sin el raise_exception=True
        # y termina derivando en un AccessError con un mensaje erroneo

        if self._raise_condition(model, mode):
            return exceptions.AccessError(_(ACCESS_ERROR_MSG))
        return super(IrModelAccess, self)._make_access_error(model, mode)

    def _get_model_name(self, model):
        if isinstance(model, models.BaseModel):
            assert model._name == "ir.model", "Invalid model object"
            model_name = model.model
        else:
            model_name = model
        return model_name

    def _raise_condition(self, model, mode):
        model_name = self._get_model_name(model)
        return mode != "read" and model_name in ["product.template", "product.product"]
