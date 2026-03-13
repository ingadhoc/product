from odoo import api, fields, models
from odoo.exceptions import UserError

# commit nuevo


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"
    # Esto esta obsoleto
    # _sql_constraints = [
    #     ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive."),
    #     (
    #         "check_selling_price",
    #         "CHECK(selling_price IS NULL OR selling_price > 0)",
    #         "The selling price must be positive.",
    #     ),
    # ]
    _order = "id desc"  # Ordenar por id descendente para mostrar los registros más recientes primero

    # Se podria poner un atributo "String" en caso de que quiera mostrar algo distinto al nombre
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Integer(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    active = fields.Boolean(default=True)
    garden_orientation = fields.Selection([("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")])
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )
    property_type_id = fields.Many2one("estate.property.type", required=True)
    field1 = fields.Char()
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
        required=True,
    )
    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id")  # Hay que poner el inverso
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        # import pdb; pdb.set_trace()
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price")) if record.offer_ids else 0.0

    @api.depends("garden")
    def _compute_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "north"
            else:
                record.garden_area = 0
                record.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("Only accepted offers can be sold.")
            record.state = "sold"

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be canceled.")
            record.state = "canceled"

    def unlink(self):
        for record in self:
            if record.state not in ("new", "canceled"):
                raise UserError("You can only delete properties in state 'New' or 'Canceled'.")
        return super().unlink()

    # Esto no me funcionaba, lo hice de otra forma arriba, sobreescribiendo unlink
    # @api.ondelete()
    # def _ondelete_restrict_sold(self):
    #     for record in self:
    #         if record.state not in ("new", "canceled"):
    #             raise UserError("You can only delete properties in state 'New' or 'Canceled'.")
