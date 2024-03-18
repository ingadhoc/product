from odoo import fields, models

class EstatePropertyTags(models.Model):
    _name = 'estate.property.tag'
    _description = 'Tags to identify properties (i.e. cozy, renovated)'
    _order = "name"
    
    name = fields.Char(required=True)
    color = fields.Integer()
    
    
