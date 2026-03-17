from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"  # Name of the model
    _description = "Ofertas de Propiedades Inmobiliarias"  # Description of the model

    price = fields.Float(string="Precio")
    status = fields.Selection(
        [("accepted", "Aceptada"), ("refused", "Rechazada")],
        string="Estado",
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Comprador", required=True)
    property_id = fields.Many2one("estate.property", string="Propiedad", required=True)
    validity = fields.Integer(string="Validez (días)", default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        string="Fecha Límite",
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = False

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = 0
