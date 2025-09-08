from odoo import api, fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    # garden_area = fields.Boolean()
    garden_area_new = fields.Float(string="Garden Area")
    active = fields.Boolean(default=True)
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    sales_man = fields.Many2one("res.partner", string="Sales man", default=lambda self: self.env.user)
    buyer = fields.Many2one("res.partner", string="Buyer")
    tags_id = fields.Many2many("estate.property.tags", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends("living_area", "garden_area_new")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area_new

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            prices = rec.offer_ids.mapped("price")
            rec.best_price = max(prices) if prices else 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area_new = 10
            self.garden_orientation = "north"
        else:
            self.garden_area_new = 0
            self.garden_orientation = 0
