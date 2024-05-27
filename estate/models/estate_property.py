from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"

    def _cmp_date_availability(self):
        return datetime.today() + relativedelta(months=+3)

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=_cmp_date_availability, string="Available From")
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(selection=[
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ])
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area
            
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = max(rec.offer_ids.mapped("price"))
            
            
    @api.onchange('garden')
    def _onchange_garden(self):
        for rec in self:
            if rec.garden:
                rec.garden_area = 10
                rec.garden_orientation = 'north'
            else:
                rec.garden_area = False
                rec.garden_orientation = False

