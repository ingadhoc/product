from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    cron = env.ref("product_planned_price.ir_cron_update_price_from_planned", raise_if_not_found=False)
    if cron:
        cron.code = """
# Este cron actualiza los precios de ventas desde el precio planeado.
model.cron_update_prices_from_planned()
"""
        cron.write({"code": cron.code})
