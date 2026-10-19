from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductAttributeTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.size = cls.env["product.attribute"].create(
            {"name": "Size", "value_ids": [(0, 0, {"name": "S"}), (0, 0, {"name": "M"})]}
        )
        cls.color = cls.env["product.attribute"].create({"name": "Color", "value_ids": [(0, 0, {"name": "Red"})]})
        cls.template = cls.env["product.attribute.template"].create(
            {"name": "T-shirts", "product_attribute_ids": [(6, 0, (cls.size | cls.color).ids)]}
        )
        cls.product_empty = cls.env["product.template"].create(
            {"name": "T-shirt A", "product_attribute_template_id": cls.template.id}
        )
        cls.product_with_size = cls.env["product.template"].create(
            {
                "name": "T-shirt B",
                "product_attribute_template_id": cls.template.id,
                "attribute_line_ids": [
                    (0, 0, {"attribute_id": cls.size.id, "value_ids": [(6, 0, cls.size.value_ids[:1].ids)]})
                ],
            }
        )

    def _lines(self, product):
        return {line.attribute_id: line.value_ids for line in product.attribute_line_ids}

    def test_update_attributes_adds_missing_lines_empty(self):
        self.template.update_attributes()
        self.assertEqual(
            self._lines(self.product_empty),
            {self.size: self.env["product.attribute.value"], self.color: self.env["product.attribute.value"]},
        )
        self.assertEqual(
            self._lines(self.product_with_size),
            {self.size: self.size.value_ids[:1], self.color: self.env["product.attribute.value"]},
        )
        self.assertEqual(self.template.not_configured_product_qty, 2)

    def test_buttons_do_not_filter_by_sale_ok(self):
        # the counters count every product of the template, so the lists must not add "To sell"
        action = self.template.action_view_not_configured_products()
        self.assertEqual(
            action["context"],
            {
                "search_default_product_attribute_template_id": self.template.id,
                "search_default_attributes_not_configured": 1,
            },
        )
