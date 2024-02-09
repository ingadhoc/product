from odoo import fields, models, api
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offers'
    _order = "price desc"


    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse= '_inverse_date_deadline')


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add(record.create_date, days=record.validity) if record.create_date else False
                

    def _inverse_date_deadline(self):
        for record in self.filtered('date_deadline'):
            create_date = (record.create_date or fields.Datetime.now()).date()
            record.validity = (record.date_deadline - create_date).days


    @api.model
    def create(self, vals):

        res = super(EstatePropertyOffer, self).create(vals)

        existing_offer = self.search([
            ('property_id', '=', vals.get('property_id')),
            ('price', '>', vals.get('price')),
        ], limit=1)

        if existing_offer:
            raise UserError("Cannot create an offer with a lower price than an existing one.")

        self.env['estate.property'].browse(vals.get('property_id')).write({'state':'offer_received'})

        return res


    def action_button_refuse(self):
        for record in self:
            if self.status == 'accepted':
                raise UserError ('Cannot refuse an accepted offer')
            else:
                record.status = 'refused'
        return True
    

    def action_button_accept(self):
        for record in self:
            if 'accepted' in record.property_id.offer_ids.mapped('status'):
                raise UserError ('Cannot accept more than one offer')
            else:
                record.status = 'accepted'
                record.property_id.state = 'offer_accepted'
                record.property_id.selling_price = record.price
                record.property_id.partner_id = record.partner_id
        return True
    

    @api.constrains('price')
    def _check_offer_price(self):
        for record in self:
            if record.price < 0:
                raise UserError('The Offer Price should be positive.')

