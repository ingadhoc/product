from unittest.mock import patch

import psycopg2
from odoo.service.model import MAX_TRIES_ON_CONCURRENCY_FAILURE
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

_RETRY_LOGGER = "odoo.addons.product_replenishment_cost.models.product_template"


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.ProductTemplate = self.env["product.template"]
        self.ResCurrency = self.env["res.currency"]
        self.ProductSupplierInfo = self.env["product.supplierinfo"]
        self.ResPartner = self.env["res.partner"]
        self.ReplenishmentCostRule = self.env["product.replenishment_cost.rule"]

        self.currency1 = self.ResCurrency.create({"name": "CUR1", "symbol": "**C1**", "rate": 1.0})
        self.currency2 = self.ResCurrency.create({"name": "CUR2", "symbol": "**C2**", "rate": 1.5})

        self.replenishment_cost_rule = self.ReplenishmentCostRule.create(
            {"name": "Test Rule", "item_ids": [(0, 0, {"sequence": 1, "percentage_amount": 10.0})]}
        )

        self.supplier = self.ResPartner.create(
            {
                "name": "Test Supplier",
            }
        )

        self.product_template = self.ProductTemplate.create(
            {
                "name": "Test Product",
                "standard_price": 100.0,
                "replenishment_base_cost": 80.0,
                "replenishment_base_cost_currency_id": self.currency1.id,
                "replenishment_cost_type": "manual",
                "replenishment_cost_rule_id": self.replenishment_cost_rule.id,
            }
        )

        def test_compute_replenishment_cost(self):
            self.product_template._compute_replenishment_cost()
            self.assertEqual(self.product_template.replenishment_cost, 80.0)
            self.assertEqual(self.product_template.replenishment_base_cost_on_currency, 80.0)

        def test_compute_supplier_data(self):
            self.supplier_info1 = self.ProductSupplierInfo.create(
                {
                    "product_tmpl_id": self.product_template.id,
                    "partner_id": self.supplier.id,
                    "currency_id": self.currency1.id,
                    "net_price": 120.0,
                    "last_date_price_updated": "2024-01-01",
                }
            )
            self.supplier_info2 = self.ProductSupplierInfo.create(
                {
                    "product_tmpl_id": self.product_template.id,
                    "partner_id": self.supplier.id,
                    "currency_id": self.currency2.id,
                    "net_price": 100.0,
                    "last_date_price_updated": "2024-08-01",
                }
            )

            self.product_template.replenishment_cost_type = "last_supplier_price"
            self.product_template._compute_supplier_data()

            self.assertEqual(self.product_template.supplier_price, 100.0)
            self.assertEqual(self.product_template.supplier_currency_id, self.currency2)

        def test_replenishment_cost_last_update(self):
            initial_update_time = self.product_template.replenishment_cost_last_update

            self.product_template.write({"replenishment_base_cost": 90.0})
            self.product_template._compute_replenishment_cost()

            new_update_time = self.product_template.replenishment_cost_last_update

            self.assertNotEqual(new_update_time, initial_update_time)
            self.assertGreater(new_update_time, initial_update_time)


class TestUpdateCostFromReplenishmentCost(TransactionCase):
    def setUp(self):
        super(TestUpdateCostFromReplenishmentCost, self).setUp()
        self.ProductTemplate = self.env["product.template"]
        self.product_template = self.ProductTemplate.create(
            {
                "name": "Test Product",
                "standard_price": 100.0,
                "replenishment_base_cost": 80.0,
                "replenishment_base_cost_currency_id": self.env.ref("base.USD").id,
                "replenishment_cost_type": "manual",
                "currency_id": self.env.ref("base.EUR").id,
            }
        )

    def test_update_cost_from_replenishment_cost(self):
        product = self.env["product.product"].create(
            {
                "product_tmpl_id": self.product_template.id,
                "standard_price": 100.0,
                "currency_id": self.env.ref("base.EUR").id,
            }
        )

        self.product_template._update_cost_from_replenishment_cost()

        self.assertEqual(product.standard_price, 80.0)


class TestCronUpdateCostRetry(TransactionCase):
    """Reintento del cron ante errores de concurrencia de PostgreSQL.

    No se puede provocar un SerializationFailure real de forma determinística, así que
    inyectamos la falla parcheando el helper propio ``_cron_update_cost_from_replenishment_cost``
    (no primitivas del ORM). La escritura real del batch ya está cubierta por
    ``TestUpdateCostFromReplenishmentCost``; acá validamos solo el control de reintentos.
    Además parcheamos ``cr.rollback`` (el framework de tests lo prohíbe) y ``time.sleep``
    para no penalizar la corrida.
    """

    @mute_logger(_RETRY_LOGGER)
    def test_cron_retries_and_succeeds_on_serialization_failure(self):
        ProductTemplate = self.env["product.template"]
        calls = {"n": 0}

        def _flaky(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise psycopg2.errors.SerializationFailure()
            return True

        with patch.object(
            type(ProductTemplate),
            "_cron_update_cost_from_replenishment_cost",
            side_effect=_flaky,
        ), patch.object(self.env.cr, "rollback", lambda: None), patch("time.sleep", lambda *args: None):
            result = ProductTemplate.cron_update_cost_from_replenishment_cost(company_ids=[self.env.company.id])

        # un fallo transitorio + un reintento exitoso
        self.assertEqual(calls["n"], 2)
        self.assertTrue(result)

    @mute_logger(_RETRY_LOGGER)
    def test_cron_reraises_after_max_retries(self):
        ProductTemplate = self.env["product.template"]
        calls = {"n": 0}

        def _always_fail(*args, **kwargs):
            calls["n"] += 1
            raise psycopg2.errors.SerializationFailure()

        with patch.object(
            type(ProductTemplate),
            "_cron_update_cost_from_replenishment_cost",
            side_effect=_always_fail,
        ), patch.object(self.env.cr, "rollback", lambda: None), patch("time.sleep", lambda *args: None):
            with self.assertRaises(psycopg2.errors.SerializationFailure):
                ProductTemplate.cron_update_cost_from_replenishment_cost(company_ids=[self.env.company.id])

        # se agotan los MAX_TRIES intentos antes de relanzar
        self.assertEqual(calls["n"], MAX_TRIES_ON_CONCURRENCY_FAILURE)


class TestCronUpdateCostAllBatches(TransactionCase):
    """Una corrida del cron tiene que recorrer todos los batches pendientes.

    Antes procesaba uno solo y encolaba el resto con un trigger, así que una pasada completa
    dependía de N corridas encadenadas.
    """

    PARAMETER = "product_replenishment_cost.last_updated_record_id"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.products = cls.env["product.template"].create(
            [
                {
                    "name": "CRON BATCH %s" % index,
                    "replenishment_cost_type": "manual",
                    "replenishment_base_cost": 10.0 + index,
                    "replenishment_base_cost_currency_id": cls.company.currency_id.id,
                }
                for index in range(4)
            ]
        )

    def test_cron_processes_every_pending_batch(self):
        self.products.product_variant_ids.with_company(self.company).standard_price = 0.0
        # arrancamos el cursor justo antes de nuestros productos, que son los últimos creados
        self.env["ir.config_parameter"].sudo().set_param(self.PARAMETER, str(min(self.products.ids) - 1))
        self.env.invalidate_all()

        # batch_size=1 fuerza un batch por producto. El commit por batch lo neutralizamos porque
        # el framework de tests lo prohíbe.
        with patch.object(self.env.cr, "commit", lambda: None):
            self.env["product.template"]._cron_update_cost_from_replenishment_cost(
                company_ids=[self.company.id], batch_size=1
            )

        for index, template in enumerate(self.products):
            self.assertEqual(template.product_variant_id.with_company(self.company).standard_price, 10.0 + index)
        self.assertEqual(
            self.env["ir.config_parameter"].sudo().search([("key", "=", self.PARAMETER)], limit=1).value,
            "0",
            "al terminar de recorrer todos los productos el cursor tiene que volver a 0",
        )
