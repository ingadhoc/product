from odoo import fields, models

class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "salesman_id") #Add a domain to the field so it only lists the available properties.
