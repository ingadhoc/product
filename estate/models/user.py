from odoo import fields, models


class User(models.Model):
    _inherit= 'res.users'

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='sales_person_id', string='')
