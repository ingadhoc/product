from odoo import fields, models


class Type(models.Model):
    _name = "estate.property.type"
    _description = "Type of Real Estate Property"

    name = fields.Char(required=True)
