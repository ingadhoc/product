from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class EstatePropertyOffer (models.Model):
    _name = "estate.property.offer"
    _description = 'Real Estate Properties Offers'
    _order = "price asc"
     
    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'),('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(string='Date Deadline', compute='_compute_date_deadline')
    # state = fields.Selection(related='property_id.state', string="Property State", readonly=True)

    @api.depends("create_date","validity") 
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = fields.Date.add(
                rec.create_date, days=rec.validity) if rec.create_date else False

    def _inverse_date_deadline(self):
        for rec in self:
            rec.validity=(rec.date_deadline - rec.create_date.date()).days

    def action_accept_offer(self):
        for record in self:
            if 'accepted' in record.property_id.offer_ids.mapped("status"):
                    raise Warning('No se puede aceptar más de una oferta')
            else:
                record.status = 'accepted'
                record.property_id.partner_id = record.partner_id
                record.property_id.selling_price = record.price
                return True

    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
        return True

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)','El precio de oferta no puede ser negativo')]

    @api.model
    def create(self, vals):
        if 'property_id' in vals:
            property = self.env['estate.property'].browse(vals['property_id'])
            property.write({'state': 'offer_accepted'})
            existing_offers = self.search([('property_id', '=', property.id)])
            max_existing_amount = max(existing_offers.mapped('price'), default=0)
            if vals.get('price', 0) <= max_existing_amount:
                raise exceptions.UserError("El monto de la oferta debe ser mayor que cualquier oferta existente para esta propiedad.")
        return super(EstatePropertyOffer, self).create(vals)
