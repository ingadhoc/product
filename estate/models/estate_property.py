from odoo import api, fields, models


class RealEstate(models.Model):
    _name = "estate.property"
    _description = "Real Estate"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), days=90))
    # date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), days=90))
    active = fields.Boolean(default=True)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    state = fields.Selection(
        string='Status', required=True, copy=False,
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        default='new')
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    total_area = fields.Integer(compute="_compute_total_area")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesman = fields.Many2one("res.users", default=lambda self: self.env.user)
    buyer = fields.Many2one("res.partner", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offer")
    best_price = fields.Float(compute='_compute_best_offer')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for rec in self:
            rec.best_price = max(rec.mapped('offer_ids.price')) if rec.offer_ids else 0

    @api.onchange('garden')
    def _onchange_garden(self):
        self.garden_area = 10 if self.garden else 0
        self.garden_orientation = 'north' if self.garden else ''


    # -------------------------------------------------------------------------
    # Notas
    # -------------------------------------------------------------------------

# import pdb; pdb.set_trace()
