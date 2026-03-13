from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offers"
    _sql_constraints = [
        ("check_offer_price", "CHECK(price > 0)", "The offer price must be strictly positive."),
    ]
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one("estate.property.type", related="property_id.property_type_id")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (
                (record.create_date + relativedelta(days=record.validity)).date() if record.create_date else False
            )

    @api.depends("date_deadline", "create_date")
    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (
                (record.date_deadline - record.create_date).days if record.date_deadline and record.create_date else 0
            )

    def action_accept(self):
        for record in self:
            if record.property_id.state not in ["new", "offer_received"]:
                raise UserError("Only new or offer received properties can accept an offer.")
            record.status = "accepted"
            record.property_id.state = "offer_accepted"
            record.property_id.selling_price = record.price
            record.property_id.partner_id = record.partner_id

    def action_reject(self):
        for record in self:
            record.status = "refused"

    @api.constrains("price", "property_id.expected_price")
    def _check_price(self):
        for record in self:
            if record.price < 0.9 * record.property_id.expected_price:
                raise UserError("The offer price must be at least 90% of the expected price.")

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # Encuentra la mayor oferta, menos la actual
            other_offers = rec.property_id.offer_ids.filtered(lambda o: o.id != rec.id)
            max_other = max(other_offers.mapped("price")) if other_offers else 0.0
            if max_other and rec.price < max_other:
                raise UserError("You cannot create an offer with a lower price than an existing offer.")

            # actualiza estado a oferta recibida si es nuevo
            if rec.property_id.state == "new":
                rec.property_id.state = "offer_received"

        return records
