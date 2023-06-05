from odoo import _, api, fields, models


class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = 'List of offers'

    name = fields.Char(string='Offer')
    price = fields.Float(string='Price')
    status = fields.Selection(string='Status', selection=[
        ('accepted', 'Accepted'), 
        ('refused', 'Refused')])
    partner_id = fields.Many2one(comodel_name='res.partner', string='Client', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', string='Property', required=True)
    validity = fields.Integer(string='Validity', default=7)
    date_deadline = fields.Date(string='Date Deadline', compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = fields.Date.add(rec.create_date, days=rec.validity) if rec.create_date else False

    def _inverse_date_deadline(self):
        for rec in self:
            if rec.create_date:
                delta_days = rec.date_deadline - rec.create_date.date()
                rec.validity = delta_days.days
            else:
                False