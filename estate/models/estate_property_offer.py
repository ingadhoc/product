from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offers"

    price = fields.Float('Price')
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused'),], copy=False,)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)
    property_id = fields.Many2one(comodel_name='estate.property', string='Property', required=True)
    validity = fields.Integer('Validity', default=7)
    date_deadline = fields.Date('Deadline', compute="_compute_deadline", inverse="_inverse_compute_deadline")

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=(record.validity))
            else:
                record.date_deadline = False
            

    def _inverse_compute_deadline(self):
        import pdb; pdb.set_trace()
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days
    


    