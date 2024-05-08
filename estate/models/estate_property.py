from odoo import models, fields, api

class EstateProperty(models.Model):
    _name = "estate_property"
    _description = "Real estate Properties"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    data_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north','North'),('south','South'),('east', 'East'),('west','West')]
    )
    total_area=fields.Float(compute="_compute_total_area")
    state=fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled') ],
        required=True,
        copy=False,
        default='new'
    )
    active=fields.Boolean(default=True) 
    property_type_id=fields.Many2one("estate_property_type", string="Property Type" )
    buyer_id=fields.Many2one("res.partner", string="Buyer")
    salesman_id=fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    tag_ids=fields.Many2many("estate_property_tag" )
    offer_ids=fields.One2many("estate_property_offer", "property_id" )
    best_price=fields.Float(compute="_compute_best_price")
 
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = False
            
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
           self.garden_area = False
           self.garden_orientation = False

