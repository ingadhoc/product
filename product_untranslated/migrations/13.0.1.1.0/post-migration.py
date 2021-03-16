from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    lang_read = env['res.lang'].search_read(['&', ('active', '=', True), ('code', '!=', 'en_US')], ['code'])
    if len(lang_read) != 1:
        # no language besides english or more than one language, no need to sync
        return True
    lang_code = lang_read[0]['code']
    models_fields = [
        ('product.template', 'description_sale'),
        ('product.template', 'description'),
    ]
    for model_name, field_name in models_fields:
        sync_field(env, lang_code, model_name, field_name)


def sync_field(env, lang_code, model_name, field_name):
    translations = env['ir.translation'].search_read([
        ('name', '=', '%s,%s' % (model_name, field_name)),
        ('type', '=', 'model'),
        ('lang', '=', lang_code)],
        ['res_id', 'value'])
    for translation in translations:
        table = model_name.replace('.', '_')
        value = translation['value']
        # sometimes translations are empty
        if not value:
            continue
        res_id = translation['res_id']
        sql_str = "UPDATE %s SET %s=%%s WHERE id=%%s" % (table, field_name)
        env.cr.execute(sql_str, (value, res_id))
