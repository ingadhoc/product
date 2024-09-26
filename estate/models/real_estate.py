from odoo import api, models, fields

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'App to manage Properties'
    
    name = fields.Char('Properties', required=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date Availability', copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3, day=1))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area(m²)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area(m²)')
    garden_orientation = fields.Selection(selection=[
        ('north','North'),
        ('south','South'),
        ('east','East'),
        ('west','West')
    ],  string='Garden Orientation')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('o_r', 'Offer Received'),
        ('o_a', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string='State', required=True, copy=False, default='new')
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string="Buyer")
    salesperson_id = fields.Many2one(string='Salesperson', comodel_name='res.users', copy=False, default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name='estate.property.tags', string='Tags')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id')
    total_area = fields.Integer(compute='_compute_total_area', string='Total Area (m²)')
    best_price = fields.Integer(compute='_compute_best_price', string='Best Price')
        
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.garden_area + rec.living_area
    
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = max(rec.offer_ids.mapped('price')) if rec.offer_ids.mapped('price') else False

    @api.onchange('garden')
    def _onchange_garden(self):
        if  self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False
    