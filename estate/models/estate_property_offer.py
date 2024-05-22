from odoo import api,fields, models
from odoo.fields import Datetime

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

    price = fields.Float('Price')
    status = fields.Selection(
        string='Status',
        selection=[('A', 'Accepted'), ('R', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer(default=7, required=True)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = Datetime.add(rec.create_date, days=rec.validity) if rec.create_date else False

    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for rec in self.filtered('date_deadline'):
            create_date = rec.create_date if rec.create_date else Datetime.now()
            rec.validity = (rec.date_deadline - create_date.date()).days