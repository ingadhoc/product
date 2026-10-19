##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductTemplateTreeFirst(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Action = cls.env["ir.actions.act_window"]
        cls.list_view = cls.env.ref("product.product_template_tree_view")

    def _modes(self, action):
        return [mode for _view_id, mode in action.views]

    def test_list_first_from_view_mode(self):
        """The list view goes first and appears only once."""
        action = self.Action.create(
            {"name": "Products", "res_model": "product.template", "view_mode": "kanban,list,form"}
        )
        self.assertEqual(self._modes(action), ["list", "kanban", "form"])
        self.assertEqual(action.view_mode, "list,kanban,form")

    def test_list_first_keeps_the_specific_view(self):
        """A list view set on the action keeps its view_id when it moves first."""
        action = self.Action.create(
            {
                "name": "Products",
                "res_model": "product.template",
                "view_mode": "kanban,list,form",
                "view_ids": [
                    (0, 0, {"sequence": 1, "view_mode": "kanban"}),
                    (0, 0, {"sequence": 2, "view_mode": "list", "view_id": self.list_view.id}),
                ],
            }
        )
        self.assertEqual(self._modes(action), ["list", "kanban", "form"])
        self.assertEqual(action.views[0][0], self.list_view.id)

    def test_core_product_action(self):
        """The product menu action of the core opens in list."""
        action = self.env.ref("product.product_template_action")
        self.assertEqual(self._modes(action)[0], "list")
        self.assertEqual(len(self._modes(action)), len(set(self._modes(action))))

    def test_no_write_when_list_is_already_first(self):
        """Reading the views again does not write view_mode when it is already right."""
        action = self.Action.create(
            {"name": "Products", "res_model": "product.template", "view_mode": "kanban,list,form"}
        )
        self.assertEqual(self._modes(action)[0], "list")
        action.invalidate_recordset(["views"])
        with patch.object(type(self.Action), "write", autospec=True, side_effect=type(self.Action).write) as write:
            self.assertEqual(self._modes(action), ["list", "kanban", "form"])
        write.assert_not_called()

    def test_other_actions_untouched(self):
        """Actions on other models, or without a list view, keep their order."""
        other_model = self.Action.create(
            {"name": "Partners", "res_model": "res.partner", "view_mode": "kanban,list,form"}
        )
        no_list = self.Action.create({"name": "Products", "res_model": "product.template", "view_mode": "kanban,form"})
        self.assertEqual(self._modes(other_model), ["kanban", "list", "form"])
        self.assertEqual(self._modes(no_list), ["kanban", "form"])
