from odoo import models,fields

class EstatePropertyType (models.Model):
    _name = "estate.property.type"
    _description = 'Real Estate Properties Types'
     
    name = fields.Char(required=True)