from odoo import api, fields, models



class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real estate property type'  
    _order = "sequence, name"   

    name = fields.Text(string='Name',required=True)
    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id', string='')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    #offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_type_id', string='Offers')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_type_id', string='Offers2')    
    offer_count = fields.Integer(compute="_compute_count_offers")

    
    _sql_constraints = [
        ('check_unique_name', 'UNIQUE(name)',
         'The property type name must be unique'),         
    ]


    @api.depends('offer_ids')
    def _compute_count_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
