from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"  # Name of the model
    _description = "Etiquetas de Propiedades Inmobiliarias"  # Description of the model

    name = fields.Char(required=True, string="Nombre")
