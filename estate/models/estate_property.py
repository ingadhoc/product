from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate properties"

    _order = "id desc"

   

    name = fields.Char('Property name', required=True)
    description = fields.Text('Description', translate=True)
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date availability', default=(datetime.today() + relativedelta(months=3)), copy=False)
    expected_price = fields.Float('Expected price', required=True)
    selling_price = fields.Float('Selling price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living area')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'),
         ('east', 'East'), ('west', 'West')]
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer received', 'Offer received'),
         ('offer accepted', 'Offer accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        default='new', required=True, copy=False)
    property_type_id = fields.Many2one(comodel_name='estate.property.type', string='Type')
    buyer_id = fields.Many2one(comodel_name='res.partner', string='Buyer', copy=False)
    salesman_id = fields.Many2one(comodel_name='res.users', string='Salesman', default=lambda self: self.env.user)
    property_tag_ids = fields.Many2many(comodel_name='estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area = fields.Float('Total area', compute="_compute_total_area")
    best_price = fields.Float('Best price', compute="_compute_best_offer")
    

    

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    

    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            if len(record.offer_ids) > 0:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
    
    @api.onchange('garden')
    def _onchange_garden_area_orientation(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False
    
    def action_property_sold(self):
        for record in self:
            if record.state != 'canceled':
                record.state = 'sold'
            else:
                raise UserError('A canceled property cannot be sold')
                

    def action_property_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
            else:
                raise UserError('A sold property cannot be canceled')

    @api.constrains('selling_price', 'expected_price')
    def _check_price_lower(self):
        for record in self:
            if record.selling_price > 0:
                if record.selling_price < (record.expected_price * 0.9):
                    raise ValidationError('The selling price must be greater than the 90 percent of the expected price')


    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state != ('new') and record.state != ('canceled') :
                raise UserError("You cannot delete a property that its not in new or canceled state.")
            


    _sql_constraints = [('check_expected_price', 'CHECK(expected_price>0)', 
    'The expected price must be greater than $0'),
    ('check_selling_price', 'CHECK(selling_price>0)', 'The selling price must be greater than $0')]