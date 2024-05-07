from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = "name asc"

    name = fields.Text(string='Name')
    color = fields.Integer(string='')
    

    _sql_constraints = [
        ('check_unique_name', 'UNIQUE(name)',
         'The property tag name must be unique'),
         
    ]
    
