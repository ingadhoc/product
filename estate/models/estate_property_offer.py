from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = "price desc"

    price = fields.Float(string='Offer')
    status = fields.Selection(string='Status', selection=[('accepted', 'Accepted'), ('refused', 'Refused'),])
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner',required=True)
    property_id = fields.Many2one(comodel_name='estate.property', string='Property',required=True)
    validity = fields.Integer(string='Validity',default=7)
    date_deadline = fields.Date(string='Deadline', compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(comodel_name='estate.property.type',related="property_id.property_type_id", string='Property Type', store=True)

    
    

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)',
         'The Offer price must be above 0')
    ]
    

    @api.model
    def create(self, values):
        # Add code here
        estate_property = self.env['estate.property'].browse(values['property_id'])
        if values['price'] < estate_property.best_price:
            raise UserError (f'The offer must be above{estate_property.best_price}')
        estate_property.state = 'offer_received'
        return super().create(values)
    

    @api.depends('create_date','validity')
    def _compute_date_deadline(self):
        for rec in self: 
            rec.date_deadline = fields.Date.add(rec.create_date, days=rec.validity) if rec.create_date else False

    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for rec in self.filtered('date_deadline'):
            create_date = rec.create_date if rec.create_date else fields.Datetime.now()
            rec.validity = (rec.date_deadline - create_date.date()).days
    
    def accept_offer(self):
        if 'accepted' not in self.property_id.offer_ids.mapped('status'):
            self.property_id.buyer_id = self.partner_id
            self.property_id.selling_price = self.price
            self.status = 'accepted'
            self.property_id.state='offer_accepted'
        else:
            raise UserError('There is an already accepted Offer')       
               
       
    def reject_offer(self):
        if self.status == 'accepted':
            self.property_id.buyer_id = False
            self.property_id.selling_price = 0
        self.status= 'refused'

    
    

    
    