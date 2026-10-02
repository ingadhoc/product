##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

from ..models.product_search_mixin import PARAM_ENABLED, PARAM_FIELDS


@tagged("post_install", "-at_install")
class TestProductSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Settings = cls.env["res.config.settings"]
        cls.tag = cls.env["product.tag"].create({"name": "amoladora chica"})
        cls.product = cls.Product.create({"name": "Angular Grinder", "default_code": "GRI-01", "barcode": "779-XYZ"})
        cls.product.product_tmpl_id.product_tag_ids = cls.tag
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.env["res.partner"].create({"name": "Vendor"}).id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_code": "V-778",
            }
        )
        cls.other = cls.Product.create({"name": "Fixed Grinder", "default_code": "GRI-02"})

    def _configure(self, *paths):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param(PARAM_ENABLED, bool(paths))
        params.set_param(PARAM_FIELDS, repr(list(paths)))

    def _settings_with(self, *paths):
        """Save the Settings page as the browser does: through the boxes."""
        values = {"product_extend_search_fields": True}
        for index, path in enumerate(paths):
            values["product_search_field_%s" % (index + 1)] = path
        return self.Settings.create(values)

    def _name_search_ids(self, model, term, **kwargs):
        return [res[0] for res in self.env[model].name_search(term, **kwargs)]

    def test_settings_round_trip(self):
        """The three boxes are saved in the parameter and read back from it."""
        settings = self._settings_with("product_tag_ids.name", "seller_ids.product_code")
        settings.execute()
        param = self.env["ir.config_parameter"].sudo().get_param(PARAM_FIELDS)
        self.assertEqual(param, repr(["product_tag_ids.name", "seller_ids.product_code"]))
        reopened = self.Settings.create({})
        self.assertEqual(reopened.product_search_field_1, "product_tag_ids.name")
        self.assertFalse(reopened.product_search_field_3)

    def test_bad_parameter_does_not_break_the_settings(self):
        """A hand edited parameter must not stop the Settings page from rendering."""
        self.assertFalse(self.Settings.new({"product_search_fields": "not a list"}).product_search_field_1)

    def test_extra_paths_in_the_parameter_block_nothing(self):
        """Four paths in the parameter: saving any setting still works, the search takes three."""
        self._configure("product_tag_ids.name", "seller_ids.product_code", "categ_id", "description_sale")
        self.Settings.create({}).execute()
        self.assertEqual(len(self.Product._extended_search_paths()), 5)

    def test_finds_by_the_configured_fields(self):
        """Tag and vendor code, on the variant and on the template, in any order."""
        self._configure("product_tag_ids.name", "seller_ids.product_code")
        self.assertIn(self.product.id, self._name_search_ids("product.product", "amoladora chica"))
        self.assertIn(
            self.product.product_tmpl_id.id,
            self._name_search_ids("product.template", "amoladora chica"),
        )
        self.assertIn(self.product.id, self._name_search_ids("product.product", "V-778"))
        self.assertIn(self.product.id, self._name_search_ids("product.product", "chica angular"))
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "chica missing"))

    def test_accepts_what_odoo_can_search(self):
        """Not stored but searchable, and a relation as the last step, both work."""
        for path, term in [
            ("barcode", "779-X"),
            ("sellers_product_code", "V-778"),
            ("product_tag_ids", "amoladora chica"),
        ]:
            self._settings_with(path).execute()
            self.assertIn(self.product.id, self._name_search_ids("product.product", term), path)

    def test_guards(self):
        """Nothing runs without configuration, under three characters, or on an exact search."""
        self._configure()
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "amoladora"))
        self.assertIn(self.product.id, self._name_search_ids("product.product", "Angular"))
        self._configure("product_tag_ids.name")
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "am"))
        self.assertFalse(self._name_search_ids("product.product", "amoladora chica", operator="="))
        with patch.object(type(self.Product), "_extended_search_domain", autospec=True) as spy:
            self.Product.name_search("Grinder", limit=1)
            spy.assert_not_called()

    def test_single_query(self):
        """Every word on every field costs one query, not one per field."""
        self._configure("product_tag_ids.name")
        product_class = type(self.Product)
        original_search = product_class._search
        calls = []

        def counting_search(self, *args, **kwargs):
            calls.append(args)
            return original_search(self, *args, **kwargs)

        with patch.object(product_class, "_search", counting_search):
            self.Product._extend_name_search([], "amoladora chica", None, "ilike", 10)
        # the other calls are the access rule checks on reading the results
        self.assertEqual(len([args for args in calls if "product_tag_ids" in str(args)]), 1)

    def test_rejects_what_cannot_be_searched(self):
        """The widget does not filter these, so the inverse has to."""
        for path in [
            "description",  # html
            "image_1920",  # attachment
            "there_is_no_such_field",
            "standard_price",  # restricted by groups
            "product_variant_id.barcode",  # the step in the middle is not searchable
        ]:
            with self.assertRaises(ValidationError, msg=path):
                self._settings_with(path)

    def test_rejects_groups_on_a_step_in_the_middle(self):
        """A path is only as accessible as its least accessible step."""
        field = self.env["product.template"]._fields["seller_ids"]
        with patch.object(field, "groups", "base.group_system"):
            with self.assertRaises(ValidationError):
                self._settings_with("seller_ids.product_code")
