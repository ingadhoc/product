from odoo import api, fields, models
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Offer to buy a property'
    _order = "price desc"
    
    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ]
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True, ondelete='cascade')
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store="True")

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)',
         'Offer price must be strictly positive')
    ]

    @api.depends("date_deadline", "validity", "partner_id")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add(
                record.create_date, days=record.validity) if record.create_date else False
            
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days

    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.partner_id = record.partner_id

            for rec in record.property_id.offer_ids:
                if rec != record:
                    rec.status = 'refused'

    def action_refuse(self):
        for record in self:
            record.status = 'refused'

    @api.model
    def create(self, vals):
        estate_property = self.env['estate.property'].browse(vals['property_id'])
        if vals['price'] < estate_property.best_price:
            raise UserError(f"The offer must be higher than {estate_property.best_price}")
        estate_property.state = 'offer_received'

        return super().create(vals)

        