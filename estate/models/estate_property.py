from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = 'Real Estate Properties'
    _order = "id desc"
     
    name = fields.Char(required=True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    tag_ids = fields.Many2many("estate.property.tag")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(),months=3), string= "Available From")
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True,copy=False)
    bedrooms = fields.Integer(default="2")
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Integer()
    garden = fields.Boolean()
    active = fields.Boolean(default=True)
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'),('east', 'East'),('west', 'West')])    
    state = fields.Selection([('new','New'), ('offer_received','Offer Received'),('offer_accepted','Offer Accepted'),('sold','Sold'),('canceled','Canceled')], required=True, copy=False, default='new')
    user_id = fields.Many2one('res.users', string='Sale person', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    total_area=fields.Float(compute="_compute_total_area")
    amount=fields.Float()
    best_price=fields.Float(compute="_compute_best_price")

    @api.depends("garden_area","living_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = max(rec.offer_ids.mapped('price') or [0])

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = False
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if  record.state == 'canceled':
                raise Warning('No puede vender una propiedad cancelada')
            record.state = 'sold'
        
    def cancel_property(self):
        for record in self:
            if  record.state == 'sold':
                raise Warning('No puede cancelar una propiedad vendida')
            record.state = 'canceled'

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price  > 0)',
         'El precio esperado no puede ser negativo'),
         ('check_selling_price', 'CHECK(selling_price  >= 0)',
         'El precio de venta de una propiedad debe ser positivo')]

    @api.constrains('selling_price', 'expected_price')
    def check_selling_price(self):
        for rec in self:
            percentage = rec.selling_price / rec.expected_price 
            if float_is_zero(rec.selling_price, precision_digits=2) is False and percentage < 0.9:
                raise ValidationError('El precio de venta no puede ser inferior al 90% del precio esperado')

    @api.model
    @api.ondelete(at_uninstall=False)
    def _check_ondelete(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise exceptions.UserError(
                "No se puede eliminar una propiedad que no esté en estado 'Nuevo' o 'Cancelado'.")
