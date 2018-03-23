# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class SalesmanGroup(models.Model):

    _name = "sale.salesman.group"
    _description = "Salesman Group"
    _order = "name"

    _constraints = [
        (models.Model._check_recursion,
         'Error ! You cannot create recursive '
         'categories.', ['parent_id'])
    ]

    @api.multi
    def name_get(self):
        if not len(self.ids):
            return []
        reads = self.read(['name', 'parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    @api.multi
    def _name_get_fnc(self):
        res = self.name_get()
        return dict(res)

    name = fields.Char('Name', required=True, translate=True)
    complete_name = fields.Char(
        compute=_name_get_fnc, string='Name')
    parent_id = fields.Many2one(
        'sale.salesman.group', 'Parent Group', select=True)
    child_id = fields.One2many(
        'sale.salesman.group', 'parent_id',
        string='Children Groups')
