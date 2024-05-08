from odoo import models, fields, api

class EstatePropertyOffer(models.Model):
    _name = "estate_property_offer"
    _description = "Real estate Property Offers"

    price=fields.Float()
    status=fields.Selection(
         selection=[('accepted','Accepted'),('refused','Refused')],
         copy=False
    )
    partner_id=fields.Many2one("res.partner", required=True)
    property_id=fields.Many2one("estate_property", required=True)
    validity=fields.Integer(default=7)
    date_deadline=fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

     ##ver! sale error cuando cambio validity
    @api.depends('validity', 'create_date')

    def _inverse_date_deadline(self):
        for rec in self:
               if rec.create_date:
                    rec.validity=(rec.date_deadline - rec.create_date.date()).days
               
    def _compute_date_deadline(self):
          for rec in self:
               if rec.create_date:
                    rec.date_deadline= fields.Date.add(rec.create_date, days = rec.validity)
               else:
                    rec.date_deadline = False

