##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    computed_list_price_manual = fields.Float(
        string='Planned Price Manual',
        digits=dp.get_precision('Product Price'),
        help='Field to store manual planned price',
    )
    computed_list_price = fields.Float(
        string='Planned Price',
        compute='_compute_computed_list_price',
        digits=dp.get_precision('Product Price'),
        help='Planned Price. This value depends on Planned Price Type" an '
        'other parameters.',
    )
    list_price_type = fields.Selection([
        ('manual', 'Fixed value')],
        string='Planned Price Type',
        # we make it optional
        # required=True,
        default='manual',
    )

    @api.model
    def cron_update_prices_from_planned(self, limit=None):
        _logger.info('Running update prices from planned cron')
        return self.with_context(
            commit_transaction=True)._update_prices_from_planned()

    @api.multi
    def _update_prices_from_planned(self):
        """
        If we came from tree list, we update only in selected list
        Despues de varias pruebas, obtuvimos la mejor pefromance de esta manera
        Haciendo practicamente lo de ahora pero sin el slice tuvimos une
        performance basatante peor (casi 2 o 3 veces mas de tiempo)
        """
        # we search again if it is called from list view
        domain = [('list_price_type', '!=', False)]
        commit_transaction = self.env.context.get('commit_transaction')
        if self:
            domain.append(('id', 'in', self.ids))

        batch_size = 1000
        product_ids = self.search(domain).ids
        sliced_product_ids = [
            product_ids[i:i + batch_size] for i in range(
                0, len(product_ids), batch_size)]
        cr = self.env.cr
        run = 0
        for product_ids in sliced_product_ids:
            run += 1
            # we make invalidate cache so that it does not do prefetch of all,
            # only the slice
            self.invalidate_cache()
            recs = self.browse(product_ids)
            _logger.info(
                'Running update prices for %s products. Run %s of %s' % (
                    len(recs), run, len(sliced_product_ids)))
            for rec in recs:
                # by using sql we win lot of performance, from 12minutes to
                # xx for 40000 products

                # el or 0.0 es porque
                # in some cases computed list price is False
                #  and this gives error
                cr.execute(
                    "UPDATE product_template SET list_price=%s WHERE id=%s",
                    (rec.computed_list_price or 0.0, rec.id))

            # commit update (fo free memory?) also to have results stored
            # in the future, if we store the date, we can update only newones

            # mainly we add this by mistake in migration but also
            # so that only the commit is done by cron
            if commit_transaction:
                cr.commit()  # pylint: disable=invalid-commit
            _logger.info('Finish updating prices of run %s' % run)
        return True

    @api.depends(
        'list_price_type',
        'computed_list_price_manual',
    )
    def _compute_computed_list_price(self):
        manual_recs = self.filtered(
            lambda x: x.list_price_type == 'manual')
        _logger.info('Get computed_list_price for %s "manual" products' % (
            len(manual_recs)))
        for rec in manual_recs:
            rec.update({'computed_list_price': rec.computed_list_price_manual})

    @api.model
    def _price_get(self, products, ptype='list_price'):
        """
        We do this so that if someone wants to force the calculated price
        be based on the planned, you can do it by sending use_planned_price
        in the context
        """
        if self._context.get('use_planned_price') and ptype == 'list_price':
            ptype = 'computed_list_price'
        return super(ProductTemplate, self)._price_get(products, ptype=ptype)
