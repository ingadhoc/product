from odoo import _, api, fields, models



class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price = fields.Float(string='Offer')
    status = fields.Selection(string='Status', selection=[('accepted', 'Accepted'), ('refused', 'Refused'),])
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner',required=True)
    property_id = fields.Many2one(comodel_name='estate.property', string='Property',required=True)
    validity = fields.Integer(string='Validity',default=7)
    date_deadline = fields.Date(string='Deadline', compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends('create_date','validity')
    def _compute_date_deadline(self):
        for rec in self: 
            rec.date_deadline = fields.Date.add(rec.create_date, days=rec.validity) if rec.create_date else False

    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for rec in self.filtered('date_deadline'):
            create_date = rec.create_date if rec.create_date else fields.Datetime.now()
            rec.validity = (rec.date_deadline - create_date.date()).days


    
    