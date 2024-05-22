from odoo import api, fields, models
from odoo.fields import Date, Datetime

class EstateProperty(models.Model):
	_name = 'estate.property'
	_description = 'Real Estate Properties'

	name = fields.Char('Name', required=True)
	description = fields.Text('Description')
	postcode = fields.Char('Postcode')
	date_availability = fields.Date('Date Availability', copy=False, default=Datetime.add(Date.today(), months=3))
	expected_price = fields.Float('Expected Price', required=True)
	selling_price = fields.Float('Selling Price', readonly=True, copy=False)
	bedrooms = fields.Integer('Bedrooms', default=2)
	living_area = fields.Integer('Living Area (sqm)')
	facades = fields.Integer('Facades')
	garage = fields.Boolean('Garage')
	garden = fields.Boolean('Garden')
	garden_area = fields.Integer('Garden Area (sqm)')
	garden_orientation = fields.Selection(
		string='Garden Orientation',
		selection=[('N','North'), ('S','South'), ('W','West'), ('E','East'), ('NW', 'NorthWest'), ('NE', 'NorthEast'), ('SW', 'SouthWest'), ('SE', 'SouthEast')]
		)
	total_area = fields.Integer('Total area', compute='_compute_total_area')
	active = fields.Boolean('Active', default=True)
	state = fields.Selection(
		string='State',
		selection=[('N', 'New'), ('OR', 'Offer Received'), ('OA', 'Offer Accepted'), ('S', 'Sold'), ('C', 'Cancelled')]
	)
	property_type_id = fields.Many2one('estate.property.type', string='Property Type')
	buyer = fields.Many2one('res.partner', string='Buyer', copy=False)
	salesman = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
	property_tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
	property_offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Property Offers')
	best_offer = fields.Float('Best Offer', compute='_compute_best_price')

	@api.depends('living_area', 'garden_area')
	def _compute_total_area(self):
		for rec in self:
			rec.total_area = rec.living_area + rec.garden_area

	@api.depends('property_offer_ids.price')
	def _compute_best_price(self):
		for rec in self:
			rec.best_offer = max(rec.property_offer_ids.mapped('price') or 0)
	
	@api.onchange('garden')
	def _onchange_garden(self):
		for rec in self:
			if rec.garden:
				rec.garden_area = 10
				rec.garden_orientation = 'N'
			else:
				rec.garden_area = rec.garden_orientation = False