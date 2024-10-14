from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"
    _order = "id desc"

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(string="Available From", default=fields.Date.today() + timedelta(days=90), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=
                                          [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=True)
    state = fields.Selection(required=True,
                             selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
                             default='new', copy=False)
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (Sqm)")
    best_price = fields.Integer(compute="_compute_best_price", string="Best Offer")

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'The expected price of a property should be positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
        'The selling price of a property should be positive.'),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):   
        for rec in self:
            if rec.offer_ids:
                rec.best_price = max(rec.offer_ids.mapped('price'))
            else:
                rec.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        self.garden_orientation = 'north' if self.garden else ''
        self.garden_area = 10 if self.garden else 0                
    
    def action_set_property_sold(self):
        for rec in self:
            if rec.state == 'cancelled':
                raise UserError('Cancelled properties cannot be sold')
        else:    
            rec.state = 'sold'

    def action_set_property_cancelled(self):
        for rec in self:
            if rec.state == 'sold':
                raise UserError('Sold properties cannot be cancelled')
            else:    
                rec.state = 'cancelled'
    
    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_cancelled(self):
        if any(rec.state in ['new','cancelled'] for rec in self):
            raise UserError("Can't delete a property with 'New' or 'Cancelled' state")
    