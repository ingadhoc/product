##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models
from odoo.exceptions import AccessError

GROUP = "price_security.group_only_view_sale_price"


class PriceSecurityHiddenCostMixin(models.AbstractModel):
    """Common part of the two ways of hiding a cost: the field list, the group
    check and taking the fields out of every view.

    A field the user cannot read has to leave the arch as well: the web client
    resolves every ``<field>`` node against the fields the view returns and
    raises "field is undefined" when one is missing. Marking it invisible is
    not enough, the node itself has to go.
    """

    _name = "price.security.hidden.cost.mixin"
    _description = "Price Security Hidden Cost Fields"

    _price_security_cost_fields = ()

    def _price_security_hides_cost(self):
        return not self.env.su and self.env.user.has_group(GROUP)

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (self.env.user.has_group(GROUP),)

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if self._price_security_hides_cost():
            self._price_security_drop_cost_nodes(arch)
        return arch, view

    @api.model
    def _price_security_drop_cost_nodes(self, arch):
        """Drop the cost fields of every model present in the arch, not only of
        `self`: an embedded x2many list carries the comodel fields inline."""
        for node in list(arch.iter("field")):
            field_name = node.get("name")
            if field_name not in self._price_security_node_cost_fields(node):
                continue
            for label in arch.xpath("//label[@for='%s']" % field_name):
                label.getparent().remove(label)
            node.getparent().remove(node)

    @api.model
    def _price_security_node_cost_fields(self, node):
        """Cost fields of the model a ``<field>`` node belongs to, walking up
        the x2many chain to find it."""
        chain = []
        parent = node.getparent()
        while parent is not None:
            if parent.tag == "field":
                chain.append(parent.get("name"))
            parent = parent.getparent()
        model = self
        for field_name in reversed(chain):
            field = model._fields.get(field_name)
            if field is None or not field.comodel_name:
                return ()
            model = self.env[field.comodel_name]
        return getattr(model, "_price_security_cost_fields", ())


class PriceSecurityCostMixin(models.AbstractModel):
    """Make cost fields unreadable instead of only hiding them on the views.

    A field hidden on a view is still readable through search_read, read_group,
    export, custom filters and the AI agent. `_has_field_access` is the hook
    every read path goes through, and it also keeps the field out of the
    prefetch, so no internal read trips over it.
    """

    _name = "price.security.cost.mixin"
    _description = "Price Security Cost Fields"
    _inherit = ["price.security.hidden.cost.mixin"]

    @api.model
    def _has_field_access(self, field, operation):
        if operation == "read" and field.name in self._price_security_cost_fields and self._price_security_hides_cost():
            return False
        return super()._has_field_access(field, operation)


class PriceSecurityPrecomputedCostMixin(models.AbstractModel):
    """Same goal, for fields the ORM reads back while writing the record.

    `sale.order.line.margin` is precomputed, so denying `_has_field_access`
    stops restricted users from creating or editing sale lines. These fields
    are instead dropped from what the client can discover and ask for, one read
    path at a time, leaving the ORM free to read them for itself.
    """

    _name = "price.security.precomputed.cost.mixin"
    _description = "Price Security Precomputed Cost Fields"
    _inherit = ["price.security.hidden.cost.mixin"]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if self._price_security_hides_cost():
            for field_name in self._price_security_cost_fields:
                res.pop(field_name, None)
        return res

    def _read_format(self, fnames, load="_classic_read"):
        res = super()._read_format(fnames, load)
        if self._price_security_hides_cost():
            for record_values in res:
                for field_name in self._price_security_cost_fields:
                    if field_name in record_values:
                        record_values[field_name] = False
        return res

    def export_data(self, fields_to_export):
        if self._price_security_hides_cost():
            self._price_security_check_specs(fields_to_export)
        return super().export_data(fields_to_export)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        if self._price_security_hides_cost():
            self._price_security_check_domain(domain)
            self._price_security_check_order(order)
        return super()._search(domain, offset, limit, order, **kwargs)

    @api.model
    def _read_group(self, domain, groupby=(), aggregates=(), having=(), offset=0, limit=None, order=None):
        if self._price_security_hides_cost():
            self._price_security_check_domain(domain)
            self._price_security_check_domain(having)
            self._price_security_check_specs(groupby)
            self._price_security_check_specs(aggregates)
            self._price_security_check_order(order)
        return super()._read_group(domain, groupby, aggregates, having, offset, limit, order)

    @api.model
    def _price_security_check_specs(self, specs):
        """`specs` are field expressions: "margin", "margin:sum", "date:month"."""
        for spec in specs or ():
            self._price_security_check_field(str(spec).split(":")[0].split(".")[0])

    @api.model
    def _price_security_check_domain(self, domain):
        for condition in domain or ():
            if isinstance(condition, (tuple, list)) and len(condition) == 3 and isinstance(condition[0], str):
                self._price_security_check_field(condition[0].split(".")[0])

    @api.model
    def _price_security_check_order(self, order):
        for term in (order or "").split(","):
            if term.strip():
                self._price_security_check_field(term.split()[0].split(".")[0])

    @api.model
    def _price_security_check_field(self, field_name):
        if field_name in self._price_security_cost_fields:
            raise AccessError(
                self.env._(
                    'You do not have enough rights to access the field "%(field)s" on %(document_model)s.',
                    field=field_name,
                    document_model=self._name,
                )
            )
