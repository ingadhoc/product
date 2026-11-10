import importlib.util

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.tools.misc import file_path

MIGRATION = "price_security/migrations/19.0.1.5.0/post-migration.py"


def load_migration():
    """Import the post-migration, which no regular import can reach: the file name
    carries a dash and the version folder is not an identifier."""
    spec = importlib.util.spec_from_file_location("price_security_post_migration", file_path(MIGRATION))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@tagged("post_install", "-at_install")
class TestAllowedRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # property_product_pricelist stays empty while the pricelist feature is off,
        # and with it the pricelist half of the restriction.
        cls.env.ref("base.user_root").group_ids += cls.env.ref("product.group_product_pricelist")
        cls.terms = cls.env["account.payment.term"].create(
            [{"name": "Allowed Restriction Term %s" % sequence, "sequence": sequence} for sequence in (91, 92, 93)]
        )
        cls.pricelists = cls.env["product.pricelist"].create(
            [{"name": "Allowed Restriction Pricelist %s" % sequence, "sequence": sequence} for sequence in (91, 92, 93)]
        )
        cls.lower_term, cls.partner_term, cls.higher_term = cls.terms
        cls.lower_pricelist, cls.partner_pricelist, cls.higher_pricelist = cls.pricelists
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Allowed Restriction Customer",
                "property_payment_term_id": cls.partner_term.id,
                # property_product_pricelist is computed from this one
                "specific_property_product_pricelist": cls.partner_pricelist.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Allowed Restriction Product", "type": "consu", "list_price": 100.0}
        )
        cls.seller = new_test_user(
            cls.env,
            login="allowed_restriction_seller",
            groups="sales_team.group_sale_salesman,price_security.group_only_view,product.group_product_pricelist",
        )

    def _create_order(self, payment_term=None, pricelist=None):
        order = (
            self.env["sale.order"]
            .with_user(self.seller)
            .create(
                {
                    "partner_id": self.partner.id,
                    "payment_term_id": (payment_term or self.partner_term).id,
                    "pricelist_id": (pricelist or self.partner_pricelist).id,
                    "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": 1})],
                }
            )
        )
        order.flush_recordset()
        return order

    def _seed_allowed(self):
        fill_allowed_from_sequence = load_migration().fill_allowed_from_sequence
        fill_allowed_from_sequence(self.terms, "payment_term_allowed_ids")
        fill_allowed_from_sequence(self.pricelists, "pricelist_allowed_ids")

    def test_partner_values_are_always_allowed(self):
        self.assertTrue(self._create_order())

    def test_empty_allowed_blocks_lower_sequence_payment_term(self):
        # What an upgraded database hits: the sequences survived but the allowed
        # lists 19.0 reads are empty, so only the term of the contact is left.
        with self.assertRaises(UserError):
            self._create_order(payment_term=self.lower_term)

    def test_empty_allowed_blocks_lower_sequence_pricelist(self):
        with self.assertRaises(UserError):
            self._create_order(pricelist=self.lower_pricelist)

    def test_seeded_allowed_accepts_lower_sequence_payment_term(self):
        self._seed_allowed()
        self.assertTrue(self._create_order(payment_term=self.lower_term))

    def test_seeded_allowed_rejects_higher_sequence_payment_term(self):
        self._seed_allowed()
        with self.assertRaises(UserError):
            self._create_order(payment_term=self.higher_term)

    def test_seeded_allowed_accepts_lower_sequence_pricelist(self):
        self._seed_allowed()
        self.assertTrue(self._create_order(pricelist=self.lower_pricelist))

    def test_seeded_allowed_rejects_higher_sequence_pricelist(self):
        self._seed_allowed()
        with self.assertRaises(UserError):
            self._create_order(pricelist=self.higher_pricelist)

    def test_seeding_keeps_ties_and_excludes_itself(self):
        tie = self.env["account.payment.term"].create({"name": "Allowed Restriction Term 92 bis", "sequence": 92})
        terms = self.terms | tie
        load_migration().fill_allowed_from_sequence(terms, "payment_term_allowed_ids")
        self.assertEqual(self.lower_term.payment_term_allowed_ids, self.env["account.payment.term"])
        self.assertEqual(self.partner_term.payment_term_allowed_ids, self.lower_term | tie)
        self.assertEqual(tie.payment_term_allowed_ids, self.lower_term | self.partner_term)
