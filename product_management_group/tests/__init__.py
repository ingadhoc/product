##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo.addons.product.tests.common import ProductCommon


# We made this monkey patch to avoid issue with other test like account and debit note that creates products
# and the group is not added to the user used to do it.
# It's not possible to fix them on the test because it's not possible load on integrations test of other module.
class ProductManagementGroupCommon(ProductCommon):
    @classmethod
    def patch_get_default_groups(cls):
        groups = super(ProductCommon, cls).get_default_groups()
        return groups | cls.env.ref('base.group_system') | cls.env.ref('product_management_group.group_products_management')

    ProductCommon.get_default_groups = patch_get_default_groups
