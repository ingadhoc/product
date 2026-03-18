from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    pricelist_item = env["product.pricelist.item"].search(
        [("compute_price", "=", "formula"), ("price_round", "=", 0.0)]
    )
    precision = env["decimal.precision"].sudo().precision_get("Product Price")
    rounding = 10**-precision
    pricelist_item.write({"price_round": rounding})
    count_rules = len(pricelist_item)

    channel_admin = env.ref("mail.channel_admin", raise_if_not_found=False)
    if channel_admin and count_rules > 0:
        channel_admin.message_post(
            body=_(
                "Hicimos una actualización automática para mejorar la precisión de las listas de precios. "
                'En las reglas de listas de precio tipo "fórmula" que no tenían una precisión de redondeo definida, '
                "aplicamos la precisión de precios configurada en su base de datos. "
                "Se ajustaron %(count)s reglas de precios."
            )
            % {"count": count_rules},
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
