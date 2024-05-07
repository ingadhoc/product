from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description ="Real Estate Property"
    _order = "id desc"

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
                                ('offer_received', 'Offer Received'),
                                ('offer_accepted', 'Offer Accepted'),
                                ('sold', 'Sold'),
                                ('canceled', 'Canceled'),
                                ],
                            default='new', 
                            readonly=True
                            )
    property_type_id = fields.Many2one(comodel_name='estate.property.type', string='Property Type')
    sales_person_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer',copy=False)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id', string='Offers')
    total_area = fields.Integer(string='Total Area',compute="_compute_total_area")
    best_price = fields.Float(string='Best Offer', compute="_compute_best_price",store =True)
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'The expected price must be above 0'),
         ('check_selling_price', 'CHECK(selling_price >= 0)',
         'The selling price must be above 0')
    ]

    

    @api.ondelete(at_uninstall=False)
    def _delete_property(self):
        for rec in self:
            if rec.state not in ['new','canceled']:
                raise UserError('You can only delete properties that are New or Canceled')


    
   
    @api.constrains('expected_price','selling_price')
    def _check_expected_price(self):
        #raise ValidationError('asdasd')
        if self.offer_ids.filtered(lambda x:x.status == 'accepted'):
            #import pdb; pdb.set_trace()
            if float_compare(self.selling_price, self.expected_price * 0.9, precision_rounding=2) < 0:
                raise ValidationError('The selling price cannot be lower tan 90% of the expected price')

    @api.depends('total_area',)
    def _compute_total_area(self):
        self.total_area = self.garden_area + self.living_area
    
    @api.depends('offer_ids','offer_ids.price')
    def _compute_best_price(self):
        if self.offer_ids :
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
    
    def sold_property(self):
        if self.state == 'canceled':
            raise UserError('Properties canceled can not be marked as sold')
        self.state='sold'

    def cancel_property(self):
        if self.state == 'sold':
            raise UserError('Properties sold can not be marked as canceled')
        self.state='canceled'

    def offer_recieved(self):
        if self.state not in ['canceled','sold','offer_accepted']:
            self.state = 'offer_received'
        else:
            raise UserError('Cannot change the state of this property')

        

    

    
    
    
        
    
        
    
    
    
    
    
    
    