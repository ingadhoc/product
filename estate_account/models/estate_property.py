from odoo import fields, models, api, Command

class EstatePropertyInherited(models.Model):
    _inherit = 'estate.property'

   
    

        
    def action_property_sold(self):

        res = super().action_property_sold()

        for record in self:
            record.env["account.move"].create(
                {
                    "partner_id" : record.buyer_id.id,
                    "move_type" : "out_invoice",
                    "invoice_line_ids" : [
                        Command.create({
                            "name" : "Administrative fee",
                            "quantity" : "1",
                            "price_unit" : "100"
                            }),
                        
                        Command.create({
                            "name" : "Property",
                            "quantity" : "1",
                            "price_unit" : record.selling_price / 100 * 6,
                            })
                    ]

                }


                )
    