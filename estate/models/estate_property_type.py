from odoo import models, fields

class EstatePropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Properties Types'

    name = fields.Char(requiered=True)