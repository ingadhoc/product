from odoo import models, fields, api

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Properties Offer'

    price =fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused'),], copy=False)
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',requiered=True)
    validity = fields.Integer(default = 7)
    date_deadline = fields.Date(compute ='_compute_date_deadline', inverse='_inverse_date_deadline')


    @api.depends('create_date','validity')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = fields.Date.add(
                rec.create_date,days =rec.validity)if rec.create_date else False

    def _inverse_date_deadline(self):
        for rec in self:
            rec.validity= (rec.date_deadline - rec.create_date.date()).days