from odoo import api, fields, models
from datetime import datetime, timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offers"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.property')
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_date_deadline", string="Deadline")
    
    @api.depends('validity')
    def _compute_date_deadline(self):
        for rec in self:
            base_date = rec.create_date if rec.create_date else datetime.today()
            rec.date_deadline = base_date + timedelta(days=rec.validity)
    
    