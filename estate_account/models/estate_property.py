from odoo import models, fields, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        partner_id = self.partner_id.id
        move_type = 'out_invoice'
        journal_id = self.env['account.journal'].search([('type', '=', 'sale')]).id
        commission_amount = self.selling_price * 0.06 if self.selling_price else 0.0

        values = {
           'partner_id': partner_id,
            'move_type': move_type,
            'journal_id': journal_id,
            'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                Command.create({
                    'name': self.name,
                    'quantity': 1,
                    'price_unit': self.selling_price or 0.0,
                    }),
                Command.create({
                    'name': 'Comisión de Venta (6%)',
                    'quantity': 1,                     
                    'price_unit': commission_amount,
                    }),
                Command.create({
                    'name': 'Gastos Administrativos',   
                    'quantity': 1,                     
                    'price_unit': 100.0,    
                    })
                ]}

        self.env['account.move'].create(values)
        print("Factura creada con partner_id:", partner_id, " y journal_id:", journal_id)
    
