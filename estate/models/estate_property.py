from odoo import _, api, fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description ="Real Estate Property"

    name = fields.Char(string='Name',required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Date Availability', copy=False,default=lambda self: fields.Date.add(fields.Date.today(),months=3))
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True,copy=False )
    bedrooms = fields.Integer(string='Bedrooms',default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    active = fields.Boolean(string='Active', default=True)    
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection(string='Garden Orientation', 
                                        selection=[ 
                                            ('north', 'North'),
                                            ('south', 'South'),
                                            ('west', 'West'),
                                            ('east', 'East')
                                            ]
                                        )
    state = fields.Selection(string='State',
                            selection=[
                                ('new', 'New'),
                                ('offer_recived', 'Offer Recived'),
                                ('offer_accepted', 'Offer Accepted'),
                                ('sold', 'Sold'),
                                ('canceled', 'Canceled'),
                                ],
                            default='new',
                            )
    property_type_id = fields.Many2one(comodel_name='estate.property.type', string='Property Type')
    sales_person_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer',copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id', string='Offers')
    total_area = fields.Integer(string='Total Area',compute="_compute_total_area")
    best_price = fields.Float(string='Best Offer', compute="_onchange_best_price")
    
    
    
    @api.depends('total_area')
    def _compute_total_area(self):
        self.total_area = self.garden_area + self.living_area
    
    @api.onchange('offer_ids')
    def _onchange_best_price(self):
        if len(self.offer_ids) > 0:
            self.best_price = max(self.offer_ids.mapped('price'))
        else:
            self.best_price = 0

    @api.onchange('garden')
    def _onchange_field_name(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation= 'north'
        else:
            self.garden_area  = False
            self.garden_orientation = False
    

    

    
    
    
        
    
        
    
    
    
    
    
    
    