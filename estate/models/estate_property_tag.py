from odoo import fields, models

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tags"

    _order = "name"

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color')
    
    
    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'The tag name must be unique')]