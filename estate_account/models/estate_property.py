from odoo import fields, models, api

class EstateProperty(models.Model):
    _inherit = "estate.property"    

    def action_button_sold(self):
        res = super(EstateProperty, self).action_button_sold()
        print("funcionaaaa!")
        return res
