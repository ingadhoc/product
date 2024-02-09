from odoo import fields, models, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Types'
    _order = "sequence, name desc"
    _sql_constraints = [
         ('type_unique', 'unique (name)','Property type name should be unique!')]

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order types")
    property_ids = fields.One2many('estate.property', 'property_type_id')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
                record.offer_count =len(record.property_ids.mapped('offer_ids'))


class EstatePropertyTypeLine(models.Model):
    _name = 'estate.property.type.line'
    _description = 'Real Estate Property Types Line'


    property_ids = fields.Many2one('estate.property.type')
    name = fields.Char()
    expected_price = fields.Float()
    state = fields.Selection([('new', 'New'), ('offer_received', 'Offer Received'),('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),('canceled', 'Canceled')],required=True, copy=False, default='new')

    