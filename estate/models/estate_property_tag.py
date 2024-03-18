from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tags'
    _order = "name desc"
    _sql_constraints = [('tag_unique', 'unique (name)','Property tag name should be unique!')]

    name = fields.Char(required=True)
    color = fields.Integer()

    # @api.constrains('name')
    # def _check_name(self):
    #     for record in self:
    #         if record.name in record.name.mapped():
    #             raise ValidationError('Property tag name should be unique!')

            


