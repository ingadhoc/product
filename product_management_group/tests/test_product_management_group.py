##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase


class TestProductManagementGroup(TransactionCase):
    """Dummy test to ensure the test folder is properly loaded"""

    def test_group_exists(self):
        """Test that the product management group exists"""
        group = self.env.ref("product_management_group.group_products_management")
        self.assertTrue(group.exists())
        self.assertEqual(group.name, "Products Management")
