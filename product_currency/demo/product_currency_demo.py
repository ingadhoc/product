import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


# pylint: disable=consider-merging-classes-inherited
# pylint: disable=R8180
class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _install_product_currency_demo(self, companies=None):
        if companies:
            for company in companies:
                _logger.info("Creating product_currency demo data for: %s", company.name)
                env = self.with_context(allowed_company_ids=[company.id]).env
                env[self._name]._load_records(self._product_currency_demo_records())
            return
        _logger.info("Creating product_currency demo data")
        self._load_records(self._product_currency_demo_records())

    @api.model
    def _product_currency_demo_records(self):
        usd_id = self.env.ref("base.USD").id
        eur_id = self.env.ref("base.EUR").id
        return [
            {
                "xml_id": "product_currency.demo_product_usd",
                "values": {
                    "name": "Product USD",
                    "type": "service",
                    "list_price": 100.0,
                    "currency_id": usd_id,
                    "force_currency_id": usd_id,
                },
                "noupdate": True,
            },
            {
                "xml_id": "product_currency.product_with_forced_currency",
                "values": {
                    "name": "Product with forced currency (EUR)",
                    "categ_id": self.env.ref("product.product_category_goods").id,
                    "standard_price": 50.0,
                    "list_price": 100.0,
                    "currency_id": usd_id,
                    "force_currency_id": eur_id,
                    "type": "consu",
                },
                "noupdate": True,
            },
        ]
