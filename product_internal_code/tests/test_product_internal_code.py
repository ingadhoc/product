##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


@tagged("post_install", "-at_install")
class TestProductInternalCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sequence = cls.env.ref("product_internal_code.sequence")
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

    def _next_code(self):
        return "%%0%sd" % self.sequence.padding % self.sequence.number_next_actual

    def test_code_from_sequence(self):
        expected = self._next_code()
        product = self.env["product.product"].create({"name": "Sequence product"})
        self.assertEqual(product.internal_code, expected)
        self.assertEqual(product.product_tmpl_id.internal_code, expected)

    def test_manual_code_is_kept(self):
        expected_next = self._next_code()
        product = self.env["product.product"].create({"name": "Manual product", "internal_code": "MANUAL-01"})
        self.assertEqual(product.internal_code, "MANUAL-01")
        self.assertEqual(self._next_code(), expected_next, "A manual code must not consume the sequence")

    def test_template_code_goes_to_variant(self):
        expected_next = self._next_code()
        template = self.env["product.template"].create({"name": "Template product", "internal_code": "TMPL-01"})
        self.assertEqual(template.product_variant_ids.internal_code, "TMPL-01")
        self.assertEqual(template.internal_code, "TMPL-01")
        self.assertEqual(self._next_code(), expected_next)

    def test_template_write_goes_to_variant(self):
        template = self.env["product.template"].create({"name": "Writable product"})
        template.internal_code = "TMPL-02"
        self.assertEqual(template.product_variant_ids.internal_code, "TMPL-02")

    def test_code_is_unique(self):
        self.env["product.product"].create({"name": "First", "internal_code": "DUP-01"})
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.env["product.product"].create({"name": "Second", "internal_code": "DUP-01"})
            self.env.flush_all()

    def test_copy_gets_new_code(self):
        product = self.env["product.product"].create({"name": "Original", "internal_code": "ORIG-01"})
        expected = self._next_code()
        duplicate = product.copy()
        self.assertEqual(duplicate.internal_code, expected)

    def test_batch_template_create(self):
        templates = self.env["product.template"].create(
            [
                {"name": "Batch A", "internal_code": "BATCH-A"},
                {"name": "Batch B"},
                {"name": "Batch C", "internal_code": "BATCH-C"},
            ]
        )
        self.assertEqual(templates.mapped("name"), ["Batch A", "Batch B", "Batch C"])
        self.assertEqual(templates[0].product_variant_ids.internal_code, "BATCH-A")
        self.assertNotIn(templates[1].product_variant_ids.internal_code, (False, "BATCH-A", "BATCH-C"))
        self.assertEqual(templates[2].product_variant_ids.internal_code, "BATCH-C")

    def test_template_create_does_not_leak_code(self):
        template = self.env["product.template"].create({"name": "Leak", "internal_code": "LEAK-01"})
        self.assertNotIn("skip_internal_code_sequence", template.env.context)
        duplicate = template.copy()
        self.assertNotIn(duplicate.product_variant_ids.internal_code, (False, "LEAK-01"))

    def test_template_code_with_variants(self):
        attribute = self.env["product.attribute"].create(
            {"name": "Size", "value_ids": [Command.create({"name": "S"}), Command.create({"name": "M"})]}
        )
        expected_next = self._next_code()
        template = self.env["product.template"].create(
            {
                "name": "Template with variants",
                "internal_code": "VAR-01",
                "attribute_line_ids": [
                    Command.create({"attribute_id": attribute.id, "value_ids": [Command.set(attribute.value_ids.ids)]})
                ],
            }
        )
        self.assertEqual(template.product_variant_ids.mapped("internal_code"), ["VAR-01", expected_next])
        self.assertEqual(
            self.sequence.number_next_actual, int(expected_next) + 1, "Only the variant without code uses the sequence"
        )
