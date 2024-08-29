from odoo import models,fields, api, exceptions
from odoo.exceptions import ValidationError

class EstatePropertyTag (models.Model):
    _name = "estate.property.tag"
    _description = 'Real Estate Properties Tags'
    _order = "name desc"
     
    name = fields.Char(string='Nombre')
    color = fields.Integer()
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'El nombre debe ser único.')]
