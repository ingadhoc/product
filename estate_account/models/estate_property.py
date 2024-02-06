from odoo import fields, models, api

class EstatePropertyInherited(models.Model):
    _inherit = 'estate.property'

    prubeaherencia = fields.Integer('PRUEBAHERENCIA')
    

        
    def action_property_sold(self):
        for record in self:
            record.env["account.move"].create(
                {
                    "partner_id" : record.buyer_id.id,
                    "move_type" : "out_invoice"
                }


                )
    