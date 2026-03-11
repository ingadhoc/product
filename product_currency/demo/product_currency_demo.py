import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


# pylint: disable=consider-merging-classes-inherited
# pylint: disable=R8180
class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _install_product_currency_demo(self):
        _logger.info("Creating product_currency demo data")
        for xml_name, model_name, values in self._product_currency_demo_records(self.env):
            self._create_demo_record(self.env, model_name, xml_name, "product_currency", values)

    @api.model
    def _product_currency_demo_records(self, env):
        """Retorna lista de (xml_name, model, values)."""
        usd_id = env.ref("base.USD").id
        return [
            (
                "demo_product_usd",
                "product.template",
                {
                    "name": "Product USD",
                    "type": "service",
                    "list_price": 100.0,
                    "currency_id": usd_id,
                    "force_currency_id": usd_id,
                },
            ),
        ]

    @api.model
    def _create_demo_record(self, env, model_name, xml_name, module, values):
        """Crea o actualiza un registro demo con su XML ID. Idempotente y forzando valores."""
        IrModelData = env["ir.model.data"]

        existing = IrModelData.search(
            [
                ("module", "=", module),
                ("name", "=", xml_name),
                ("model", "=", model_name),
            ],
            limit=1,
        )
        if existing:
            record = env[model_name].browse(existing.res_id)
            record.sudo().write(values)
        else:
            record = env[model_name].sudo().create(values)
            IrModelData.sudo().create(
                {
                    "module": module,
                    "name": xml_name,
                    "model": model_name,
                    "res_id": record.id,
                }
            )
        return record
