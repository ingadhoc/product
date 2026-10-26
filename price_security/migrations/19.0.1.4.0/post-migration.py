from odoo.upgrade import util

PRIVILEGE = "price_security.module_prices_management"
GROUPS = [
    "price_security.group_only_view",
    "price_security.group_only_view_sale_price",
]
RULES = [
    "price_security.restrict_price_read_only_payment_term",
    "price_security.restrict_price_read_only_pricelist",
    "price_security.restrict_price_read_only_pricelist_item",
]


def migrate(cr, version):
    module, name = PRIVILEGE.split(".")
    cr.execute("SELECT model FROM ir_model_data WHERE module = %s AND name = %s", [module, name])
    row = cr.fetchone()
    # Until 18.0 this xmlid was an ir.module.category and the loader refuses to repoint it to the
    # res.groups.privilege that 19.0 declares, so the stale record has to go first.
    if row and row[0] == "ir.module.category":
        util.remove_record(cr, PRIVILEGE)

    util.update_record_from_xml(cr, PRIVILEGE)
    for xmlid in GROUPS:
        util.update_record_from_xml(cr, xmlid, reset_translations=True)

    env = util.env(cr)
    for xmlid in RULES:
        # The XML adds the group with command 4, so the pre-16.0 link would survive the reload.
        env.ref(xmlid).groups = [(5, 0, 0)]
        util.update_record_from_xml(cr, xmlid)
