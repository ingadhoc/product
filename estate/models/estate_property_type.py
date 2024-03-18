from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Type of property (i.e. house, apartment)'
    _order = "name"
    
    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")    
    sequence = fields.Integer()
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_count_offers")

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The name must be unique')
    ]

    @api.depends('offer_ids')
    def _compute_count_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)