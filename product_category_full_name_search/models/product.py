# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api
from openerp.osv import expression


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            # Be sure name_search is symetric to name_get
            categories = name.split('/')
            parents = list(categories)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(
                    '/'.join(parents), args=args,
                    operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    category_ids = self.search(
                        [('id', 'not in', category_ids)])
                    domain = expression.OR(
                        [[('parent_id', 'in', category_ids)], domain])
                else:
                    domain = expression.AND(
                        [[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(categories)):
                    domain = [
                        [('name', operator, '/'.join(categories[-1 - i:]))],
                        domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            ids = self.search(
                expression.AND([domain, args]),
                limit=limit)
        else:
            ids = self.search([])
        return ids.name_get()

    @api.multi
    def name_get(self):
        res = []
        for cat in self:
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, '/'.join(reversed(names))))
        return res
