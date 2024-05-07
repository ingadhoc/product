from odoo import models , Command



class EstateProperty(models.Model):
    _inherit= 'estate.property'
    
    def sold_property(self):
        for rec in self: 
            self.env['account.move'].create({
                'partner_id': rec.buyer_id.id,
                'move_type':'out_invoice',
                'line_ids' : [
                    Command.create({
                    'name' : rec.name,
                    'price_unit' : rec.selling_price * 0.06,
                    'quantity' : 1,
                    }),
                    Command.create({
                        'name': 'Admin Fee',
                        'price_unit' : 100,
                        'quantity' :1
                    }),
                ],
            })
        return super().sold_property()
