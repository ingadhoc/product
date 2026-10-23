from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductCurrency(TransactionCase):
    def test_forced_currency_in_search_and_group(self):
        """Search and group by currency must use the forced currency, as the form does."""
        currency = self.env["res.currency"].create({"name": "TSC", "symbol": "TSC"})
        forced = self.env["product.template"].create({"name": "Forced", "force_currency_id": currency.id})
        self.env["product.template"].create({"name": "Not forced"})
        domain = [("name", "in", ["Forced", "Not forced"])]

        self.assertEqual(forced.currency_id, currency)
        self.assertEqual(self.env["product.template"].search(domain + [("currency_id", "=", currency.id)]), forced)
        groups = dict(self.env["product.template"]._read_group(domain, ["currency_id"], ["__count"]))
        self.assertEqual(groups, {currency: 1, self.env.company.currency_id: 1})
