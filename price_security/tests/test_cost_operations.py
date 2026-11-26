from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestRestrictedUserOperations(TransactionCase):
    """The cost is hidden from the user, not from the ORM.

    Taking the field away at ORM level also takes it away from the server, and
    the server needs it: the screens of a restricted user reach the cost through
    the computes that derive from it, and validating a delivery values the move
    off the product cost. These are the three flows that broke when the field
    itself was denied.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restricted_user = new_test_user(
            cls.env,
            login="price_security_operator",
            groups="base.group_user,sales_team.group_sale_salesman_all_leads,"
            "stock.group_stock_user,price_security.group_only_view_sale_price",
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Restricted cost product",
                "is_storable": True,
                "list_price": 150.0,
                "standard_price": 100.0,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.env.company.id)], limit=1)
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.warehouse.lot_stock_id, 10)

    def _read_view_fields(self, records, view_type, view_xmlid=None):
        """Read what the client reads when it opens that view"""
        view_id = view_xmlid and self.env.ref(view_xmlid).id or False
        result = records.get_views([(view_id, view_type)])
        return records.read(list(result["models"][records._name]["fields"]))

    def test_product_form_opens(self):
        """Reached the cost through parent_standard_price, of
        stock_account_multicompany_ux"""
        values = self._read_view_fields(
            self.product.product_tmpl_id.with_user(self.restricted_user),
            "form",
            "product.product_template_form_view",
        )
        self.assertFalse(values[0].get("standard_price"))

    def test_value_adjustments_opens(self):
        """Inventory > Reporting > Value Adjustments, the report of the ticket.
        Reached the cost through the computes that describe the adjustment"""
        adjustments = self.env["product.value"].search([("product_id", "=", self.product.id)])
        self.assertTrue(adjustments, "creating the product with a cost records an adjustment")
        values = self._read_view_fields(
            adjustments.with_user(self.restricted_user), "form", "stock_account.product_value_form_view"
        )
        self.assertFalse(values[0].get("value"))

    def test_outgoing_picking_is_validated(self):
        """Valuing the move reads the product cost with the user"""
        picking = (
            self.env["stock.picking"]
            .with_user(self.restricted_user)
            .create(
                {
                    "picking_type_id": self.warehouse.out_type_id.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "move_ids": [
                        (
                            0,
                            0,
                            {
                                "name": self.product.name,
                                "product_id": self.product.id,
                                "product_uom_qty": 1,
                                "product_uom": self.product.uom_id.id,
                                "location_id": self.warehouse.lot_stock_id.id,
                                "location_dest_id": self.customer_location.id,
                            },
                        )
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = 1
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(abs(picking.move_ids.sudo().value), 100.0)
