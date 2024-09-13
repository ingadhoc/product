from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class EstatePropertyType (models.Model):
    _name = "estate.property.type"
    _description = 'Real Estate Properties Types'
    _order = "name asc"
     
    name = fields.Char(required=True)
    sequence = fields.Integer()
    property_ids = fields.One2many("estate.property", "property_type_id")

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'El nombre debe ser único.')]
