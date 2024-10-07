from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Types"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    