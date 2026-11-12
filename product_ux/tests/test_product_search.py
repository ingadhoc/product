##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase, new_test_user, tagged

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

    def _two_variants(self):
        attribute = self.env["product.attribute"].create(
            {"name": "Color", "value_ids": [(0, 0, {"name": "Red"}), (0, 0, {"name": "Blue"})]}
        )
        template = self.env["product.template"].create(
            {
                "name": "Bench Grinder",
                "product_tag_ids": self.tag.ids,
                "attribute_line_ids": [(0, 0, {"attribute_id": attribute.id, "value_ids": attribute.value_ids.ids})],
            }
        )
        red, blue = template.product_variant_ids
        red.write({"default_code": "V1-AAA", "barcode": "7790111"})
        blue.write({"default_code": "V2-BBB", "barcode": "7790222"})
        return template, red, blue

    def _configure(self, *paths):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param(PARAM_ENABLED, bool(paths))
        params.set_param(PARAM_FIELDS, repr(list(paths)))

    def _settings_with(self, *paths, user=None):
        """Save the Settings page as the browser does: through the boxes."""
        values = {"product_extend_search_fields": True}
        for index, path in enumerate(paths):
            values["product_search_field_%s" % (index + 1)] = path
        settings = self.Settings.with_user(user) if user else self.Settings
        return settings.create(values)

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

    def test_settings_page_keeps_the_fields(self):
        """Opening and saving the Settings page shows the paths and does not wipe them."""
        self._configure("product_tag_ids.name", "seller_ids.product_code")
        form = Form(self.Settings)
        self.assertEqual(form.product_search_field_1, "product_tag_ids.name")
        form.save().execute()
        param = self.env["ir.config_parameter"].sudo().get_param(PARAM_FIELDS)
        self.assertEqual(param, repr(["product_tag_ids.name", "seller_ids.product_code"]))

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

    def test_variants(self):
        """A field of the variant matches that variant only, and the template finds it by a variant code."""
        template, red, blue = self._two_variants()
        self._configure("barcode")
        self.assertEqual(self._name_search_ids("product.product", "0111"), red.ids)
        self._configure("product_tag_ids.name")
        self.assertIn(template.id, self._name_search_ids("product.template", "V1-AAA amoladora"))

    def test_exact_code_stays_alone(self):
        """The native search picks an exact code on purpose: nothing is added to it."""
        self._configure("product_tag_ids.name")
        self.Product.create({"name": "Grinder Disc", "default_code": "GRI-010"})
        self.assertEqual(self._name_search_ids("product.product", "GRI-01"), self.product.ids)

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
        """Nothing runs without configuration, with the switch off, under three characters or on an exact search."""
        self._configure()
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "amoladora"))
        self.assertIn(self.product.id, self._name_search_ids("product.product", "Angular"))
        self._configure("product_tag_ids.name")
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "am"))
        # a short word is left out of the extra query instead of scanning every path with it
        self.assertIn(self.product.id, self._name_search_ids("product.product", "amoladora zz"))
        # "like" keeps telling upper from lower case, as the native search does
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "AMOLADORA", operator="like"))
        self.assertIn(self.product.id, self._name_search_ids("product.product", "amoladora", operator="like"))
        self.assertFalse(self._name_search_ids("product.product", "amoladora chica", operator="="))
        with patch.object(type(self.Product), "_extended_search_domain", autospec=True) as spy:
            self.Product.name_search("Grinder", limit=1)
            spy.assert_not_called()
        # a parameter edited by hand holds text, and "False" is not a truth
        self.env["ir.config_parameter"].sudo().set_param(PARAM_ENABLED, "False")
        self.assertNotIn(self.product.id, self._name_search_ids("product.product", "amoladora chica"))

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
            "standard_price",  # a number is not worth searching by ilike
            "product_variant_id.barcode",  # the step in the middle is not searchable
        ]:
            with self.assertRaises(ValidationError, msg=path):
                self._settings_with(path)

    def test_rejects_properties_with_their_own_reason(self):
        """The 18.0 selector offers properties, and the reason given must be the real one."""
        with self.assertRaisesRegex(ValidationError, "holds properties"):
            self._settings_with("product_properties.color")

    def test_groups_on_save_follow_the_user(self):
        """Same criterion as the search: what counts is whether this user reads the field."""
        barcode = self.env["product.template"]._fields["barcode"]
        with patch.object(barcode, "groups", "base.group_user"):
            self._settings_with("barcode")
        # a path is only as accessible as its least accessible step
        user = new_test_user(self.env, login="product_search_admin", groups="base.group_system")
        seller_ids = self.env["product.template"]._fields["seller_ids"]
        with patch.object(seller_ids, "groups", "base.group_multi_company"):
            with self.assertRaises(ValidationError):
                self._settings_with("seller_ids.product_code", user=user)

    def test_settings_check_only_what_changes(self):
        """A path nobody touched, or a search that is off, does not block saving."""
        self._configure("seller_ids.product_code")
        user = new_test_user(self.env, login="product_search_editor", groups="base.group_system")
        seller_ids = self.env["product.template"]._fields["seller_ids"]
        with patch.object(seller_ids, "groups", "base.group_multi_company"):
            self._settings_with("seller_ids.product_code", "product_tag_ids.name", user=user)
        self.Settings.create({"product_extend_search_fields": False, "product_search_field_1": "description"})

    def test_skips_a_path_this_user_cannot_search(self):
        """What the user cannot reach is skipped, never raised, and the other paths keep working."""
        self._configure("product_tag_ids.name", "seller_ids.product_code")
        user = new_test_user(self.env, login="product_search_probe", groups="base.group_user")
        product = self.Product.with_user(user)

        def ids(term):
            return [res[0] for res in product.name_search(term)]

        self.assertIn(self.product.id, ids("amoladora chica"))
        tag_field = self.env["product.template"]._fields["product_tag_ids"]
        with patch.object(tag_field, "groups", "base.group_system"):
            self.assertFalse(ids("amoladora chica"))
            self.assertIn(self.product.id, ids("V-778"))
        self.env["ir.model.access"].search([("model_id.model", "=", "product.tag")]).unlink()
        self.assertFalse(ids("amoladora chica"))
        self.assertIn(self.product.id, ids("V-778"))
        # a path the parameter kept but Odoo cannot search never reaches the SQL either
        for path in ["no_such_field", "warranty.no_such_field", "pricelist_price"]:
            self._configure(path)
            self.assertFalse(ids("amoladora chica"))
