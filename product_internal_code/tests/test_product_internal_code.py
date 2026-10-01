##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductInternalCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # created one by one on purpose: a single create() of several coded
        # templates hits an unrelated defect of the module
        template = cls.env["product.template"]
        cls.coded = template.create({"name": "Internal Code Product", "internal_code": "IC-5432"})
        # its name carries the code of the one above, so the native search finds it first
        cls.named = template.create({"name": "IC-5432 Cable"})
        # the native search finds this one by name, and the code would find it again
        cls.both = template.create({"name": "IC-7777", "internal_code": "IC-7777"})

    def test_internal_code_finds_the_product_first(self):
        """The code finds the product first, exactly, and takes nothing from the native result."""
        with self.subTest("the code finds the template"):
            results = self.env["product.template"].name_search("IC-5432")
            self.assertIn(self.coded.id, [res[0] for res in results])
        with self.subTest("the code finds the variant, which is what an order line picks"):
            results = self.env["product.product"].name_search("IC-5432")
            self.assertIn(self.coded.product_variant_id.id, [res[0] for res in results])
        with self.subTest("part of the code does not find the product"):
            results = self.env["product.template"].name_search("IC-543")
            self.assertNotIn(self.coded.id, [res[0] for res in results])
        with self.subTest("a product the native search already found is not repeated"):
            ids = [res[0] for res in self.env["product.template"].name_search("IC-7777")]
            self.assertEqual(ids.count(self.both.id), 1)
        with self.subTest("the exact code takes the only suggestion the limit allows"):
            results = self.env["product.template"].name_search("IC-5432", limit=1)
            self.assertEqual([res[0] for res in results], [self.coded.id])
