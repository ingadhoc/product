##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models
from odoo.exceptions import AccessError
from odoo.fields import Domain
from odoo.modules import module as odoo_module

PRODUCT_MODELS = ("product.template", "product.product")
GROUP_XMLID = "product_management_group.group_products_management"


def _in_foreign_test():
    # Other modules' BaseCommon tests run as a test user without the group
    test = odoo_module.current_test
    return bool(test) and not type(test).__module__.startswith("odoo.addons.product_management_group.")


def restrict_product_access(model, operation, domain):
    """Deny any write operation on products to users outside the module group."""
    if operation != "read" and not model.env.user.has_group(GROUP_XMLID) and not _in_foreign_test():
        return Domain.FALSE
    return domain


class IrAccess(models.Model):
    _inherit = "ir.access"

    def _make_model_access_error(self, model_name, operation):
        if operation != "read" and model_name in PRODUCT_MODELS and not self.env.user.has_group(GROUP_XMLID):
            return AccessError(
                self.env._(
                    "Sorry, you are not allowed to manage products. Only users with "
                    "'Products Management' level are currently allowed to do that"
                )
            )
        return super()._make_model_access_error(model_name, operation)
