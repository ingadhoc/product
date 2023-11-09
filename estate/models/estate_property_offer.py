from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('validity')
    def _compute_date_deadline(self):

        for rec in self:
            if rec.create_date:
                rec.date_deadline = fields.Date.add(rec.create_date, days=rec.validity)
            else:
                rec.date_deadline = fields.Date.add(fields.Date.today(), days=rec.validity)

    def _inverse_date_deadline(self):
        for rec in self:
            rec.validity = (rec.date_deadline - rec.create_date.date()).days
