##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCostRevaluation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        # cuenta de valuación (activo), cuenta de revaluación (resultado) y diario
        cls.acc_valuation = cls.env["account.account"].create(
            {"name": "Stock Valuation", "code": "REVVAL", "account_type": "asset_current"}
        )
        cls.acc_cost_reval = cls.env["account.account"].create(
            {"name": "Cost Revaluation", "code": "REVCRA", "account_type": "expense"}
        )
        cls.stock_journal = cls.env["account.journal"].create(
            {"name": "Stock Journal REV", "code": "REVSJ", "type": "general", "company_id": cls.company.id}
        )
        cls.company.account_stock_journal_id = cls.stock_journal

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    # ------------------------------------------------------------------ helpers
    def _categ(self, cost_method, valuation, revaluation_account=True):
        vals = {
            "name": "Categ %s %s" % (cost_method, valuation),
            "property_cost_method": cost_method,
            "property_valuation": valuation,
            "property_stock_valuation_account_id": self.acc_valuation.id,
            "property_stock_journal": self.stock_journal.id,
        }
        if revaluation_account:
            vals["property_cost_revaluation_account_id"] = self.acc_cost_reval.id
        return self.env["product.category"].create(vals)

    def _product(self, categ, price=10.0, qty=10.0):
        product = self.env["product.product"].create(
            {
                "name": "Producto %s" % categ.name,
                "type": "consu",
                "is_storable": True,
                "categ_id": categ.id,
                "standard_price": price,
            }
        )
        # stock recién después de fijar el costo inicial (sin stock no postea)
        self.env["stock.quant"]._update_available_quantity(product, self.stock_location, qty)
        # qty_available es computado no-almacenado y su depends no incluye los quants:
        # invalidamos para que el siguiente acceso lo recalcule desde el quant creado.
        product.invalidate_recordset()
        self.assertEqual(product.qty_available, qty, "El stock on hand de prueba no quedó registrado")
        return product

    def _journal_moves_count(self):
        return self.env["account.move"].search_count([("journal_id", "=", self.stock_journal.id)])

    # -------------------------------------------------------------------- tests
    def test_revaluation_standard_realtime(self):
        product = self._product(self._categ("standard", "real_time"))
        before = self._journal_moves_count()
        # 10 -> 15 con 10 unidades => delta 50 (sube el activo)
        product.standard_price = 15.0
        moves = self.env["account.move"].search([("journal_id", "=", self.stock_journal.id)])
        self.assertEqual(len(moves) - before, 1, "Standard real_time debe generar asiento")
        move = moves.sorted("id")[-1]
        self.assertEqual(move.state, "posted")
        # Debe Valuación / Haber Diferencia de precio
        self.assertAlmostEqual(move.line_ids.filtered(lambda l: l.account_id == self.acc_valuation).debit, 50.0, 2)
        self.assertAlmostEqual(move.line_ids.filtered(lambda l: l.account_id == self.acc_cost_reval).credit, 50.0, 2)

    def test_revaluation_average_realtime(self):
        # AVCO: el cambio de standard_price también es una revaluación
        product = self._product(self._categ("average", "real_time"))
        self.assertEqual(product.cost_method, "average")
        before = self._journal_moves_count()
        # 10 -> 8 con 10 unidades => delta -20 (baja el activo)
        product.standard_price = 8.0
        moves = self.env["account.move"].search([("journal_id", "=", self.stock_journal.id)])
        self.assertEqual(len(moves) - before, 1, "AVCO real_time debe generar asiento")
        move = moves.sorted("id")[-1]
        self.assertEqual(move.state, "posted")
        # costo bajó => Haber Valuación / Debe Diferencia de precio
        self.assertAlmostEqual(move.line_ids.filtered(lambda l: l.account_id == self.acc_valuation).credit, 20.0, 2)
        self.assertAlmostEqual(move.line_ids.filtered(lambda l: l.account_id == self.acc_cost_reval).debit, 20.0, 2)

    def test_no_entry_without_revaluation_account(self):
        # sin cuenta de revaluación configurada => no se postea (lógica scrap)
        product = self._product(self._categ("standard", "real_time", revaluation_account=False))
        before = self._journal_moves_count()
        product.standard_price = 15.0
        self.assertEqual(
            self._journal_moves_count(),
            before,
            "Sin cuenta de revaluación no debe generar asiento",
        )

    def _pending_variation(self, product):
        # diferencia que el reporte/cierre de Valoración de inventario sugeriría postear
        # sobre la cuenta de valuación: valuación teórica (total_value) vs. saldo contable.
        company = self.company
        accounts_by_product = company._get_accounts_by_product(products=product)
        inventory = company.stock_value(accounts_by_product)
        accounting = company.stock_accounting_value(accounts_by_product)
        return {acc: inventory.get(acc, 0.0) - accounting.get(acc, 0.0) for acc in inventory.keys() | accounting.keys()}

    def test_no_suggested_entry_on_valuation_account(self):
        # nuestro asiento mueve la cuenta de valuación en la misma magnitud que el costo,
        # así que la variación pendiente sobre la cuenta de valuación queda igual que antes
        # (no aparece variación nueva en esa pata del cierre/reporte).
        product = self._product(self._categ("standard", "real_time"))  # costo 10, qty 10
        pending_before = self._pending_variation(product)

        product.standard_price = 15.0  # +50 sobre la cuenta de valuación

        pending_after = self._pending_variation(product)
        for acc in set(pending_before) | set(pending_after):
            delta = pending_after.get(acc, 0.0) - pending_before.get(acc, 0.0)
            self.assertTrue(
                self.company.currency_id.is_zero(delta),
                "El cambio de costo no debe agregar variación pendiente en %s (delta %s)" % (acc.code, delta),
            )

    def test_no_entry_fifo_realtime(self):
        # FIFO: standard_price es informativo, no revalúa => sin asiento
        product = self._product(self._categ("fifo", "real_time"))
        self.assertEqual(product.cost_method, "fifo")
        before = self._journal_moves_count()
        product.standard_price = 20.0
        self.assertEqual(
            self._journal_moves_count(), before, "FIFO no debe generar asiento por cambio de standard_price"
        )

    def test_no_entry_periodic_category(self):
        # categoría periódica => el ajuste lo materializa el cierre, no este flujo
        product = self._product(self._categ("standard", "periodic"))
        self.assertEqual(product.valuation, "periodic")
        before = self._journal_moves_count()
        product.standard_price = 15.0
        self.assertEqual(self._journal_moves_count(), before, "Categoría periódica no debe generar asiento")

    def test_no_entry_without_stock(self):
        # sin stock on hand no debe generarse asiento aunque cambie el costo
        categ = self._categ("standard", "real_time")
        product = self.env["product.product"].create(
            {
                "name": "Producto Sin Stock",
                "type": "consu",
                "is_storable": True,
                "categ_id": categ.id,
                "standard_price": 10.0,
            }
        )
        before = self._journal_moves_count()
        product.standard_price = 15.0
        self.assertEqual(self._journal_moves_count(), before, "Sin stock on hand no debe generar asiento")
