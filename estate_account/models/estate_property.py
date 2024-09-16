from odoo import models, Command

class InheritedEstateProperty(models.Model):
    _inherit="estate.property"

    def action_sell_property(self):
        for record in self:
            self.env['account.move'].create({
                'partner_id': record.partner_id.id,
                'move_type': 'out_invoice',
                'line_ids': [
                    Command.create({
                        "name": record.name,
                        "price_unit": record.selling_price * 0.06,
                        "quantity": 1
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "price_unit": 100.00,
                        "quantity": 1
                    })
                ]
            })

        return super().action_sell_property()