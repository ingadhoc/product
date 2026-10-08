##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo.addons.base.models.ir_actions_report import IrActionsReport
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductUx(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Product UX Wholesale"})
        cls.template = cls.env["product.template"].create({"name": "Product UX Drill", "list_price": 100.0})
        cls.product = cls.template.product_variant_id
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": cls.template.id,
                "compute_price": "discount",
                "price_discount": 10.0,
            }
        )
        cls.report = cls.env["ir.actions.report"]

    def _labels_data(self, copies, rows=1, columns=1):
        return {
            "labels": [{"name": f"Label {i}", "copies": qty} for i, qty in enumerate(copies)],
            "label_template": "product.barcode_2x7_label",
            "layout": {"rows": rows, "columns": columns},
        }

    # Labels in batches

    def test_label_batches_split_copies_and_keep_order(self):
        """Copies are cut across batches so no batch exceeds the size, and the
        labels come out in the same order and with the same total copies."""
        data = self._labels_data([3, 250, 1])
        batches = self.report._label_batches(data, 100)

        self.assertEqual([sum(label["copies"] for label in batch["labels"]) for batch in batches], [100, 100, 54])
        flat = [label["name"] for batch in batches for label in batch["labels"] for _copy in range(label["copies"])]
        self.assertEqual(flat, ["Label 0"] * 3 + ["Label 1"] * 250 + ["Label 2"])
        self.assertTrue(all(batch["layout"] == data["layout"] for batch in batches))
        self.assertEqual(len(data["labels"]), 3, "the original data is not modified")

    def test_label_batches_skip_labels_without_copies(self):
        batches = self.report._label_batches(self._labels_data([0, 2]), 100)
        self.assertEqual([label["name"] for label in batches[0]["labels"]], ["Label 1"])

    def _render_labels(self, report_xmlid, data):
        """Render with the base PDF rendering mocked: returns the labels each
        wkhtmltopdf call got and the merged result."""
        calls = []

        def fake_render(report_self, report_ref, res_ids=None, data=None):
            calls.append(sum(label["copies"] for label in data["labels"]))
            return f"pdf{len(calls)}".encode(), "pdf"

        with (
            patch.object(IrActionsReport, "_render_qweb_pdf", fake_render),
            patch(
                "odoo.addons.product_ux.models.ir_actions_report.merge_pdf",
                side_effect=lambda contents: b"|".join(contents),
            ),
        ):
            result = self.report._render_qweb_pdf(report_xmlid, data=data)
        return calls, result

    def test_dymo_labels_render_in_batches_of_pages(self):
        self.env["ir.config_parameter"].sudo().set_int("product_ux.dymo_label_batch_size", 200)
        calls, result = self._render_labels("product.action_report_product_label_dymo", self._labels_data([450]))
        self.assertEqual(calls, [200, 200, 50])
        self.assertEqual(result, (b"pdf1|pdf2|pdf3", "pdf"))

    def test_sheet_labels_render_in_batches_of_whole_pages(self):
        """A 2x7 sheet holds 14 labels: a batch of 30 labels is cut to 2 whole pages (28)."""
        self.env["ir.config_parameter"].sudo().set_int("product_ux.dymo_label_batch_size", 30)
        calls, _result = self._render_labels(
            "product.action_report_product_label_pdf", self._labels_data([300], rows=7, columns=2)
        )
        self.assertEqual(calls, [28] * 10 + [20])

    def test_sheet_labels_batch_smaller_than_a_page_renders_one_page(self):
        self.env["ir.config_parameter"].sudo().set_int("product_ux.dymo_label_batch_size", 10)
        calls, _result = self._render_labels(
            "product.action_report_product_label_pdf", self._labels_data([30], rows=12, columns=4)
        )
        self.assertEqual(calls, [30])

    def test_label_batching_can_be_disabled(self):
        self.env["ir.config_parameter"].sudo().set_int("product_ux.dymo_label_batch_size", 0)
        calls, _result = self._render_labels("product.action_report_product_label_dymo", self._labels_data([450]))
        self.assertEqual(calls, [450])

    def test_labels_rendered_as_html_are_not_batched(self):
        """In tests the PDF falls back to HTML: the labels come out in a single
        render instead of trying to merge HTML as PDF."""
        self.env["ir.config_parameter"].sudo().set_int("product_ux.dymo_label_batch_size", 2)
        labels = self._labels_data([5])
        labels["labels"][0].update(barcode_value="", barcode_text="")
        labels["label_template"] = "product.barcode_dymo_label"
        content, report_type = self.report._render_qweb_pdf("product.action_report_product_label_dymo", data=labels)
        self.assertEqual(report_type, "html")
        self.assertEqual(content.decode().count("Label 0"), 5)

    # Pricelists

    def test_surcharge_rules_round_to_price_precision(self):
        """Surcharge rules round by default; discount rules do not, so they stay
        plain discounts and sales keep showing the discount."""
        rounding = 10 ** -self.env["decimal.precision"].precision_get("Product Price")
        item = self.env["product.pricelist.item"].new({"pricelist_id": self.pricelist.id, "compute_price": "fixed"})

        item.compute_price = "discount"
        item._onchange_compute_price()
        item.price_discount = 10.0
        self.assertEqual(item.price_round, 0.0)
        self.assertTrue(item.is_plain_discount, "sales show the discount of this rule")

        item.compute_price = "markup"
        item._onchange_compute_price()
        self.assertAlmostEqual(item.price_round, rounding)

        item.price_round = 1.0
        item.compute_price = "discount"
        item._onchange_compute_price()
        item.compute_price = "markup"
        item._onchange_compute_price()
        self.assertEqual(item.price_round, 1.0, "a rounding set by hand is kept")

        item.compute_price = "fixed"
        item._onchange_compute_price()
        self.assertEqual(item.price_round, 0.0)

    def test_contextual_pricelist_by_name_list_or_id(self):
        Template = self.env["product.template"]
        for value in (self.pricelist.name, [self.pricelist.id], self.pricelist.id):
            with self.subTest(pricelist=value):
                self.assertEqual(Template.with_context(pricelist=value)._get_contextual_pricelist(), self.pricelist)
        self.assertFalse(Template.with_context(pricelist="No such pricelist")._get_contextual_pricelist())
        self.assertFalse(Template.with_context(pricelist=[])._get_contextual_pricelist())

    def test_pricelist_price_follows_the_pricelist_in_context(self):
        for pricelist in (self.pricelist.name, self.pricelist.id):
            with self.subTest(pricelist=pricelist):
                self.assertAlmostEqual(self.template.with_context(pricelist=pricelist).pricelist_price, 90.0)
                self.assertAlmostEqual(self.product.with_context(pricelist=pricelist).pricelist_price, 90.0)

    def test_pricelist_item_count(self):
        self.assertEqual(self.pricelist.item_count, 1)
        self.assertEqual(self.env["product.pricelist"].create({"name": "Empty"}).item_count, 0)

    # Products and units

    def test_search_product_by_vendor_product_code(self):
        vendor = self.env["res.partner"].create({"name": "Product UX Vendor"})
        self.env["product.supplierinfo"].create(
            {"partner_id": vendor.id, "product_tmpl_id": self.template.id, "product_code": "UX-VND-001"}
        )
        found = self.env["product.template"].search([("sellers_product_code", "=", "UX-VND-001")])
        self.assertEqual(found, self.template)

    def test_archiving_a_product_is_tracked(self):
        self.template.action_archive()
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertTrue(
            self.template.message_ids.filtered(lambda message: message.message_type == "tracking"),
            "archiving leaves a tracking message in the chatter",
        )

    def test_uom_default_search_view_searches_by_description(self):
        arch = self.env["uom.uom"].get_views([(False, "search")])["views"]["search"]["arch"]
        self.assertIn("description", arch)
        self.assertIn('name="inactive"', arch, "the native Archived filter is kept")
