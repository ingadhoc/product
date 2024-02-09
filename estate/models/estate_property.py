from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

class EstateProperty(models.Model):

    _name = 'estate.property'
    _description = 'Real Estate Property Model'
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True,)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [('north','North'),('south', 'South'), ('east', 'East'), ('west','West')])
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'), 
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
        ],required=True, copy=False, default='new')
    property_type_id = fields.Many2one('estate.property.type')
    tag_ids = fields.Many2many('estate.property.tag')
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    offer_ids = fields.One2many('estate.property.offer','property_id')
    total_area = fields.Float(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price')
    

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area= record.living_area + record.garden_area
            
            
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
                record.best_price = max(record.offer_ids.mapped('price') or [0])

    @api.onchange('garden')
    def _onchange_garden(self):
            if self.garden:
                self.garden_area = 10
                self.garden_orientation = 'north'
            else:
                self.garden_area = False
                self.garden_orientation = False


    def action_button_cancel(self):
        for record in self:
            if self.state == 'sold':
                raise UserError ('A sold property cannot be canceled')
            else:
                record.state = 'canceled'
        return True
    

    def action_button_sold(self):
        for record in self:
            if self.state == 'canceled':
                raise UserError ('A canceled property cannot be sold')
            else:
                record.state = 'sold'
        return True

    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if record.expected_price < 0:
                raise ValidationError('The Expected Price should be positive.')


    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < 0:
                raise ValidationError('The Selling Price should be positive.')


    @api.constrains('selling_price', 'expected_price', 'offer_ids.price', 'offer_ids.status')
    def _check_offer_selling_price(self):
        for record in self:
            if 'accepted' in record.offer_ids.mapped('status') and record.selling_price >= 0 and record.expected_price > 0:
                    min_selling_price = 0.9*record.expected_price
                    if float_utils.float_compare(record.selling_price, min_selling_price, precision_digits=2) == -1:
                        raise ValidationError(
                        'Selling Price should be higher than 90 percent of the Expected Price. Reduce the expected price if you want accept this offer')


    @api.ondelete(at_uninstall=False)
    def _unlink_if_property_new_canceled(self):
        for record in self:
            if record.state in ('offer_received','offer_accepted','sold'):
                raise UserError("Can't delete an active property!")


#2024-02-02 20:53:56,630 442 WARNING real_estate odoo.models: method estate.property._check_offer_selling_price: @constrains parameter 'offer_ids.price' is not a field name 
#2024-02-02 20:53:56,630 442 WARNING real_estate odoo.models: method estate.property._check_offer_selling_price: @constrains parameter 'offer_ids.status' is not a field name 
# to_do: Make the estate.property.tag list views editable. 
# state in property list view make it invisible?
# status in property offer list view make it invisible?
# chapter 12: stat button on estate.property.type pointing to the estate.property.offer action??
# use the type="action" attribute
# At this point, clicking on the stat button should display all offers. 
# We still need to filter out the offers. On the estate.property.offer action, add a domain that defines property_type_id as equal to the active_id (= the current record                                       
# chapter 13: Add the property_ids field to the base.view_users_form in a new notebook page.                   
