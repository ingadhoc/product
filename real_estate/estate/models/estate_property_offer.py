from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offers"

    price = fields.Float()
    status = fields.Selection(
        string="status",
        copy=False,
        selection=[('accepted','Accepted'),('refused','Refused')],
        )
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',required=True)

    #exercise validity date for offers chapter 8
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

# Where date_deadline is a computed field which is defined as the sum of two fields from the offer: the create_date and the validity. 
    @api.depends('create_date','validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date: 
               record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                False
#otra opc:
    # def _compute_date_deadline(self):
    #     for record in self:
    #         if record.create_date: 
    #            record.date_deadline = fields.Date.add(record.create_date, days=record.validity)
    #         else:
    #             False

# #Define an appropriate inverse function so that the user can set either the date or the validity.
    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                False