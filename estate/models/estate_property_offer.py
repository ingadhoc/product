from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused'),],
                             copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)',
         'The price of an offer should be positive.'),
    ]

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = fields.Date.add(rec.create_date, days=rec.validity) if rec.create_date else fields.Date.today()
    
    def _inverse_date_deadline(self):
        for rec in self:
            rec.validity = (rec.date_deadline - rec.create_date.date()).days
    
    def action_accept(self):
        for rec in self:
            if 'accepted' in rec.property_id.offer_ids.mapped('status'):
                raise UserError('Cannot accept more than one offer')
            
            else:
                self._check_selling_price()
                rec.status = 'accepted'
                rec.property_id.selling_price = rec.price
                rec.property_id.buyer_id = rec.partner_id
                rec.property_id.state = 'offer_accepted'

    def action_refuse(self):
        for rec in self:
            rec.status = 'refused'
            rec.property_id.selling_price = 0
            rec.property_id.buyer_id = ''

    
    @api.constrains('property_id.selling_price')
    def _check_selling_price(self):
        for rec in self:
            if rec.price < (rec.property_id.expected_price * 0.9):
                raise ValidationError("The selling price must be at least 90% of the expected price! You must reduce the expected price if you want to accept this offer.")

    @api.model
    def create(self, vals):
        self.env['estate.property'].browse(vals['property_id']).state = 'offer_received'
        return super().create(vals)
