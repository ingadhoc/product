##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo import api, fields, models
from odoo.modules.db import FunctionStatus
from odoo.tools import create_index

_logger = logging.getLogger(__name__)

# Nombre propio, distinto del que genera el registry para el btree del campo
# (product_product__default_code_index). Es lo que hace que el -u no lo toque:
# el registry solo evalua los indices que nombra el mismo, asi que no lo ve
# stale ni lo recrea. Tarea 59012.
DEFAULT_CODE_TRIGRAM_INDEX = "product_product__default_code_trgm_index"


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "default_code, name, id"

    def init(self):
        super().init()
        create_index(
            self.env.cr,
            indexname="is_favorite_idx",
            tablename="product_product",
            expressions=["is_favorite"],
            where="is_favorite IS TRUE",
        )
        self._create_default_code_trigram_index()

    @api.model
    def _create_default_code_trigram_index(self):
        """Indice trigram en default_code, ademas del btree que ya existe.

        El buscador de productos es el paso mas caro de las bases con catalogo
        grande, y el ILIKE sobre default_code no tiene indice que lo sirva: el
        btree del campo solo resuelve el "=". Medido sobre 545k productos, el
        ILIKE pasa de 218-264 ms a 0,96 ms.

        Por que a mano y no con index="trigram" en el campo: el registry no
        suma un indice, detecta que el que ya esta es de otro metodo (btree
        contra gin), lo borra y lo recrea como trigram, sin CONCURRENTLY. Y
        gin_trgm_ops no le sirve al planner para el "=", que es el primer paso
        de la cascada y el que usa cualquier sincronizacion de catalogo para
        ubicar productos: pasaria de 0,3 ms a 110 ms con Seq Scan. Van los dos
        indices, cada uno con su nombre.

        En una base con catalogo grande conviene crearlo antes del -u, que
        create_index respeta si ya existe:

            CREATE INDEX CONCURRENTLY product_product__default_code_trgm_index
                ON product_product USING gin (unaccent(default_code) gin_trgm_ops);

        Tarea 59012.
        """
        registry = self.env.registry

        if not registry.has_trigram:
            _logger.warning(
                "Sin pg_trgm en la base: no se crea %s. El ILIKE sobre "
                "default_code va a seguir resolviendose con Seq Scan.",
                DEFAULT_CODE_TRIGRAM_INDEX,
            )
            return

        # El ORM aplica unaccent() a la columna en cada (=)ilike siempre que la
        # funcion este presente, pero solo puede meterla en un indice si es
        # IMMUTABLE. Con PRESENT y no INDEXABLE, el indice saldria sin unaccent
        # y la consulta no lo usaria: preferimos no crear nada antes que dejar
        # un indice que ocupa espacio y no entra en ningun plan.
        if registry.has_unaccent != FunctionStatus.INDEXABLE:
            _logger.warning(
                "unaccent %s en la base: no se crea %s, porque el indice "
                "quedaria sin unaccent y las busquedas no lo usarian.",
                "ausente" if not registry.has_unaccent else "presente pero no IMMUTABLE",
                DEFAULT_CODE_TRIGRAM_INDEX,
            )
            return

        # Misma expresion que armaria el registry para un index="trigram", para
        # que coincida con la que genera el ORM del lado de la consulta.
        column = '"default_code"'
        expression = f"{registry.unaccent(column)} gin_trgm_ops"
        create_index(
            self.env.cr,
            indexname=DEFAULT_CODE_TRIGRAM_INDEX,
            tablename="product_product",
            expressions=[expression],
            method="gin",
        )

    active = fields.Boolean(tracking=True)
    pricelist_price = fields.Float(compute="_compute_product_pricelist_price", digits="Product Price")
    is_favorite = fields.Boolean(related="product_tmpl_id.is_favorite", readonly=True, store=True)

    @api.depends_context("pricelist", "quantity", "uom", "date", "no_variant_attributes_price_extra")
    def _compute_product_pricelist_price(self):
        for product in self:
            product.pricelist_price = product._get_contextual_price()
