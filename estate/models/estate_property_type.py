from odoo import fields, models, api

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property types"

    _order = "sequence"

    name = fields.Char('Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default="1")
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer('Offers count', compute='compute_offers')
    
    @api.depends('offer_ids')
    def compute_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    def action_show_offers(self):
        self.ensure_one()
        return {
            'name': 'Offers',
            'view_mode': 'tree,form',
            'res_model': 'estate.property.offer',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('property_type_id','=', self.id)],
          
        }

    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'The property type must be unique')]
    