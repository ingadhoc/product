##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_cost_revaluation_account_id = fields.Many2one(
        "account.account",
        string="Cost Revaluation Account",
        company_dependent=True,
        ondelete="restrict",
        check_company=True,
        help="Cuenta de resultado (contrapartida) del asiento de revaluación de inventario "
        "que se genera al cambiar el costo contable (standard_price) de productos con "
        "valoración perpetua. Si no se define, no se genera el asiento.",
    )
