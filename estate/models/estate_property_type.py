from odoo import models, fields


class Estate_property_type(models.Model):
    _name = 'estate.property.type'
    _description = 'Tipo de propiedades'

    name = fields.Char(required=True)
