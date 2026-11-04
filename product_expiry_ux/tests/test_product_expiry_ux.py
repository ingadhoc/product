from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.addons.stock.tests.common import TestStockCommon
from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestProductExpiryUx(TestStockCommon):
    # Since 20.0 every test runs as the user built from _test_user_groups, and
    # the parent only grants the product manager group: creating lots and
    # receipts needs the inventory one too.
    _test_user_groups = (
        "product.group_product_manager",
        "stock.group_stock_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # One frozen "now" for the whole scenario: no fixed dates anywhere.
        cls.now = fields.Datetime.now()
        cls.expiry_product = cls.ProductObj.create(
            {
                "name": "Yogurt",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
                "expiration_time": 10,
                "use_time": 5,
                "removal_time": 2,
                "alert_time": 6,
            }
        )
        # A second expiring product, to hold a lot with the same name.
        cls.other_product = cls.ProductObj.create(
            {
                "name": "Queso",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
                "expiration_time": 40,
                "use_time": 20,
                "removal_time": 10,
                "alert_time": 15,
            }
        )
        # The expiration date is only editable on the line when the operation
        # type does not force picking an existing lot.
        cls.picking_type_in.use_existing_lots = False

    def _new_lot(self, name):
        return self.LotObj.create({"name": name, "product_id": self.expiry_product.id})

    def _dates(self, lot):
        return (lot.expiration_date, lot.use_date, lot.removal_date, lot.alert_date)

    def _new_receipt_line(self, lot):
        picking = self.PickingObj.create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move = self.MoveObj.create(
            {
                "product_id": self.expiry_product.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        line = self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "picking_id": picking.id,
                "product_id": self.expiry_product.id,
                "quantity": 1,
                "lot_id": lot.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        return move, line

    def _set_expiration_on_line(self, move, expiration_date):
        """Type the expiration date on the line, as a user does on screen."""
        with Form(move, view="stock.view_stock_move_operations") as move_form:
            with move_form.move_line_ids.edit(0) as line_form:
                line_form.expiration_date = expiration_date

    def test_is_alert_date(self):
        """Dado un lote de un producto con caducidad, cuando su fecha de alerta
        ya pasó, entonces `is_alert_date` prende; con una alerta futura o sin
        alerta, no. Es lo que muestra el badge "Expiration Alert" del lote.
        """
        lot = self._new_lot("L-ALERT")
        cases = [
            ("la alerta ya pasó", self.now - relativedelta(days=1), True),
            ("la alerta es futura", self.now + relativedelta(days=1), False),
            ("el lote no tiene alerta", False, False),
        ]
        for label, alert_date, expected in cases:
            with self.subTest(label):
                # alert_date is stored + readonly=False, and _compute_dates only
                # depends on product_id/expiration_date: the write sticks.
                lot.write({"alert_date": alert_date})
                self.assertEqual(lot.alert_date, alert_date)
                self.assertEqual(lot.is_alert_date, expected)

    def test_onchange_expiration_date_recalcula_fechas_del_lote(self):
        """Dado la línea de una recepción con lote, cuando se cambia la
        caducidad en la línea, entonces el lote queda con esa caducidad y
        recalcula retiro y consumo con los tiempos del producto; la alerta se
        completa solo si estaba vacía, y ningún otro lote se toca.
        """
        lot = self._new_lot("L-ONCHANGE")
        untouched = self._new_lot("L-UNTOUCHED")
        twin = self.LotObj.create({"name": lot.name, "product_id": self.other_product.id})
        untouched_dates = self._dates(untouched)
        twin_dates = self._dates(twin)
        move, _line = self._new_receipt_line(lot)
        expiration = self.now + relativedelta(days=30)

        with self.subTest("la caducidad nueva recalcula retiro y consumo con los tiempos del producto"):
            lot.write({"alert_date": self.now + relativedelta(days=3)})
            previous_alert = lot.alert_date
            self._set_expiration_on_line(move, expiration)
            self.assertEqual(lot.expiration_date, expiration)
            self.assertEqual(lot.removal_date, expiration - relativedelta(days=2))
            self.assertEqual(lot.use_date, expiration - relativedelta(days=5))

        with self.subTest("un lote que ya tenía alerta la conserva"):
            self.assertEqual(lot.alert_date, previous_alert)

        with self.subTest("un lote sin alerta la recibe desde la caducidad"):
            lot.write({"alert_date": False})
            later = expiration + relativedelta(days=7)
            self._set_expiration_on_line(move, later)
            self.assertEqual(lot.alert_date, later - relativedelta(days=6))

        with self.subTest("el lote del nombre es uno solo y otro nombre queda intacto"):
            same_name = self.LotObj.search([("name", "=", lot.name), ("product_id", "=", self.expiry_product.id)])
            self.assertEqual(len(same_name), 1)
            self.assertEqual(self._dates(untouched), untouched_dates)

        with self.subTest("el lote con el mismo nombre de otro producto queda intacto"):
            self.assertEqual(self._dates(twin), twin_dates)
