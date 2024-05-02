from odoo import _, api, fields, models



class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real estate property type'

    name = fields.Text(string='Name',required=True)
    