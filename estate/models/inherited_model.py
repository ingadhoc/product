from odoo import models, fields

class Users(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "user_id", 
                                   string="Properties")
