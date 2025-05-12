from odoo import api,models,fields

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    name = fields.Char(string="Property Name", required=True)
    description = fields.Text()
    property_type_id = fields.Many2one("estate.property.type", string="Property Type", required=True)
    user_id = fields.Many2one("res.users", string="Salesperson", required=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    postcode = fields.Char()
    date_availability = fields.Date(string="Available from", copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False) 
    bedrooms = fields.Integer(default=2)
    living_area = fields.Float(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Float()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string="Garden Orientation")
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], default='new', copy=False)
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    property_offer_ids = fields.One2many("estate.property.offer", "property_id", string="Property Offers")
    active = fields.Boolean(default=True)
    
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends('living_area', 'garden_area', 'garden')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + (rec.garden_area if rec.garden else 0.0)
    
    @api.depends('property_offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            best_price = 0.0
            for offer in rec.property_offer_ids:
                if offer.price > best_price:
                    best_price = offer.price
            rec.best_price = best_price
    
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = False