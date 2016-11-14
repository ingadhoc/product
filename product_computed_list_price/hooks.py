# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
# from openerp import models, fields, api
# import cStringIO
# from openerp import tools
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def post_init_hook(cr, pool):
    """
    Seteamos computed_list_price en todos los items donde este setado
    list_price
    """
    item_ids = pool['product.pricelist.item'].search(
        cr, SUPERUSER_ID, [('base', '=', 'list_price')])
    pool['product.pricelist.item'].write(
        cr, SUPERUSER_ID, item_ids, {'base': 'computed_list_price'})
    return True
