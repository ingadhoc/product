from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offers"

    _order = "price desc"

    price = fields.Float('Price')
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused'),], copy=False,)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', string='Property', required=True)
    validity = fields.Integer('Validity', default=7)
    date_deadline = fields.Date('Deadline', compute="_compute_deadline", inverse="_inverse_compute_deadline")
    property_type_id = fields.Many2one(related='property_id.property_type_id', stored="True")
    

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=(record.validity))
            else:
                record.date_deadline = False
            

    def _inverse_compute_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.date_deadline: datetime.now()

    def action_accept_offer(self):
        for record in self:
            if 'accepted' in record.property_id.offer_ids.mapped('status'):
                raise UserError('There is already an accepted offer')
            else:
                    record.status = 'accepted'
                    record.property_id.buyer_id = record.partner_id
                    record.property_id.selling_price = record.price
            
    def action_decline_offer(self):
        for record in self:
            record.status = 'refused'

    @api.model
    def create(self,vals):
        if vals.get("property_id") and vals.get("price"):
            property = self.env["estate.property"].browse(vals["property_id"])
            property.state = 'offer received'
            if property.offer_ids:
                max_offer = max(property.mapped("offer_ids.price"))
                if vals.get("price") < max_offer:
                    raise UserError("The offer must be higher than %s" % max_offer)
        return super().create(vals)



    _sql_constraints = [('check_offer_price', 'CHECK(price>0)', 'The offer price mus be greater than $0')]
            

    