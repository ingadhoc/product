from odoo import models, fields

class  EstatePropertyTag (models.Model):
    _name  =  "estate.property.tag"
    _description  =  "Properties Tags"
    
    name = fields.Char(required=True)
