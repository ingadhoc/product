from odoo.upgrade import util


def migrate(cr, version):
    xmlid = "product.product_pricelist_item_form_view"
    util.update_record_from_xml(cr, xmlid, force_create=False)
