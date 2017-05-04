# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # TODO this field should be move to PRC (product_replenishment_cost)
    replenishment_cost_last_update = fields.Datetime(
        'Replenishment Cost Last Update',
        track_visibility='onchange',
    )
    # TODO this field should be move to PRC (product_replenishment_cost)
    replenishment_base_cost = fields.Float(
        'Replenishment Base Cost',
        digits=dp.get_precision('Product Price'),
        track_visibility='onchange',
        help="Replanishment Cost expressed in 'Replenishment Base Cost "
        "Currency'."
    )
    replenishment_base_cost_currency_id = fields.Many2one(
        'res.currency',
        'Replenishment Base Cost Currency',
        auto_join=True,
        track_visibility='onchange',
        help="Currency used for the Replanishment Base Cost."
    )
    # TODO borrar, ya lo cambiamos en nustro modulo base de rep cost
    # lo que si dejamos es sobreescribir el metodo de computar, algo que
    # deberiamos mejorar tmb
    replenishment_cost = fields.Float(
        compute='_get_replenishment_cost',
    )
    # for now we make replenshiment cost field only on template and not in
    # product (this should be done in PRC)
    #     string='Replenishment Cost',
    #     store=False,
    #     digits=dp.get_precision('Product Price'),
    #     help="The cost that you have to support in order to produce or "
    #          "acquire the goods. Depending on the modules installed, "
    #          "this cost may be computed based on various pieces of "
    #          "information, for example Bills of Materials or latest "
    #          "Purchases."

    @api.model
    def cron_update_cost_from_replenishment_cost(self):
        # como es property no podemos hacer el search
        _logger.info('Running cron update cost from replenishment')
        domain = [
            ('replenishment_base_cost', '!=', False),
            ('replenishment_base_cost_currency_id', '!=', False),
        ]
        # el prefetch nos dio una mejora de 57 contra 46 segs para 1500 prods
        return self.with_context({'prefetch_fields': False}).search(
            domain)._update_cost_from_replenishment_cost()

    @api.multi
    def _update_cost_from_replenishment_cost(self):
        _logger.info(
            'Running update cost from replenishment for %s products' % (
                len(self.ids)))
        for rec in self:
            # TODO ver si lo storearon o mejoraron para poder incluirlo
            # no hacemos mas la comparación porque tira la performance muy
            # abajo porque es campo calculado que a su vez usa properties
            # if rec.cost_method != 'standard' or not rec.replenishment_cost:
            if not rec.replenishment_cost:
                continue
            rec.standard_price = rec.replenishment_cost
        return True

    @api.multi
    @api.constrains(
        'replenishment_base_cost',
        'replenishment_base_cost_currency_id',
    )
    def update_replenishment_cost_last_update(self):
        self.write({'replenishment_cost_last_update': fields.Datetime.now()})

    @api.multi
    # TODO ver si necesitamos borrar estos depends o no, por ahora
    # no parecen afectar performance y sirvern para que la interfaz haga
    # el onchange, pero no son fundamentales porque el campo no lo storeamos
    @api.depends(
        'currency_id',
        'replenishment_base_cost',
        # because of being stored
        'replenishment_base_cost_currency_id.rate_ids.rate',
        # and this if we change de date (name field)
        'replenishment_base_cost_currency_id.rate_ids.name',
    )
    def _get_replenishment_cost(self):
        _logger.info(
            'Getting replenishment cost currency for ids %s' % self.ids)
        for rec in self:
            rec.replenishment_cost = rec.get_replenishment_cost_currency()

    @api.multi
    def get_replenishment_cost_currency(self):
        self.ensure_one()
        from_currency = self.replenishment_base_cost_currency_id
        to_currency = self.currency_id
        replenishment_cost = False
        if from_currency and to_currency:
            replenishment_cost = self.replenishment_base_cost
            if from_currency != to_currency:
                replenishment_cost = from_currency.compute(
                    replenishment_cost, to_currency, round=False)
        return replenishment_cost


# al final, directamente lo cambiamos en product.template en el modulo
# base, para mejorar temas de performance
# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     # we make it related to prod template because for now we want it only
#     # on prod template
#     replenishment_cost = fields.Float(
#         related='product_tmpl_id.replenishment_cost',
#         store=False,
#     )
