from odoo import fields, models


class Estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description = 'Tags de Propiedades inmobiliarias'

    name = fields.Char(required=True)
