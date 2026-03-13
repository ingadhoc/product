from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        # marca la propiedad como sold
        res = super().action_sold()

        # Crea un invoice por cada propiedad vendida
        for record in self:
            partner = record.partner_id and record.partner_id.id or False
            if not partner:
                # si no tiene vendedor, no se crea invoice
                continue

            price = float(record.selling_price or 0.0)
            commission = round(price * 0.06, 2)
            admin_fee = 100.00

            vals = {
                "partner_id": partner,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Commission (6% of selling price)",
                            "quantity": 1.0,
                            "price_unit": commission,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Administrative fees",
                            "quantity": 1.0,
                            "price_unit": admin_fee,
                        }
                    ),
                ],
            }

            self.env["account.move"].create(vals)

        return res
