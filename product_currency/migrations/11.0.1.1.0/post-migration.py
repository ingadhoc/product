from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    companies = env['res.company'].search([])
    for company in companies:
        for product in env['product.product'].with_context(
                force_company=company.id).search([
                    ('force_currency_id', '!=', company.currency_id.id),
                    ('force_currency_id', '!=', False),
                ]):
            standard_price = product.currency_id.compute(
                product.standard_price, company.currency_id)
            product.standard_price = standard_price
