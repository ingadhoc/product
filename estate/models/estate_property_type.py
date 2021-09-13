from odoo import models, fields

class  EstatePropertyType (models.Model):
    _name  =  "estate.property.type"
    _description  =  "Properties Types"
    
    name = fields.Char(required=True)
