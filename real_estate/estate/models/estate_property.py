from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"

    name = fields.Char('Name',required=True)
    description = fields.Text('Description')
    property_type_id= fields.Many2one("estate.property.type")
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: (datetime.now() + relativedelta(months=3)))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean('Garage')
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Jardin Area')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north','North'), ('south','South'), ('east','East'),('west','West')])
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        string='Estado',
        selection=[('new','New'),('offer_received','Offer Received'),('offer_accepted','Offer Accepted'),('sold','Sold'),('cancelled','Cancelled')],
        required=True,
        copy=False,
        default="new"
        )
    buyer_id = fields.Many2one("res.partner", copy=False) #en odoo se usaria mas partner_id
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user) #en odoo se usaria mas user_id
    # un campo many2one por convencion se indica con sufijo _id
    tag_ids = fields.Many2many('estate.property.tag')
    # many2many fields have the _ids suffix
    offer_ids = fields.One2many("estate.property.offer", "property_id")

    # Exercise total area chapter 8
    total_area = fields.Float(compute='_compute_total_area')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    # Exercise best offer chapter 8
    best_offer = fields.Float(compute='_compute_best_offer')

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price') or [0])

    
    # Error:   max(record.offer_ids.mapped('price')) devuelve una lista, si es vacia da el siguiente error:
    # File "/home/odoo/custom/repositories/real_estate/estate/models/estate_property.py", line 55, in _compute_best_offer
    # record.best_offer = max(record.offer_ids.mapped('price'))
    # ValueError: max() arg is an empty sequence

    # Exercise garden area and orientation chapter 8
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False