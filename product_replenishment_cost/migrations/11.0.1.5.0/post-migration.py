from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # products without replenishment cost currency
    domain = [
        ('replenishment_cost_type', '=', 'manual'),
        ('replenishment_base_cost', '!=', False),
        ('replenishment_base_cost', '!=', 0.0),
        ('replenishment_base_cost_currency_id', '=', False),
    ]
    currency = env.user.company_id.currency_id
    env['product.template'].search(domain)._write(
        {'replenishment_base_cost_currency_id': currency.id})
