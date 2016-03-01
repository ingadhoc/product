# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from . import product


def set_default_code(cr):

    cr.execute("""
        UPDATE product_product
        SET default_code='/'
        WHERE default_code IS NULL
        """)
