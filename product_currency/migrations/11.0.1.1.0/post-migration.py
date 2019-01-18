from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    companies = env['res.company'].search([])
    products = env['product.product'].search([])
    for company in companies:
        for product in products.filtered(
                lambda x: x.currency_id != company.currency_id):
            standard_price = product.currency_id.compute(product.with_context(
                force_company=company.id).standard_price, company.currency_id)
            product.with_context(
                force_company=company.id).standard_price = standard_price
