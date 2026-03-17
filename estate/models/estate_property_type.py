from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"  # Name of the model
    _description = "Tipos de Propiedades Inmobiliarias"  # Description of the model

    name = fields.Char(required=True, string="Nombre")
