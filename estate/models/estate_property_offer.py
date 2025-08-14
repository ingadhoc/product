from datetime import timedelta

from odoo import api, fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.offer"
    _description = "Offers received for properties"

    price = fields.Float()
    status = fields.Selection(string="Status", selection=[("accepted", "Accepted"), ("refused", "Refused")])
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("real_estate", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_date_deadline")

    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for rec in self:
            base_date = rec.create_date.date() if rec.create_date else fields.Date.today()
            rec.date_deadline = base_date + timedelta(days=rec.validity)

    def _inverse_date_deadline(self):
        for rec in self:
            if rec.date_deadline:
                base_date = rec.create_date.date() if rec.create_date else fields.Date.today()
                rec.validity = (rec.date_deadline - base_date).days
