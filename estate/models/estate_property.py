from odoo import api, fields, models

# import pdb


class EstateProperty(models.Model):
    _name = "estate.property"  # Name of the model
    _description = "Propiedades inmobiliarias"  # Description of the model

    name = fields.Char(required=True, string="Nombre")
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.add(fields.Date.today(), months=3),
        string="Fecha de Disponibilidad",
    )
    expected_price = fields.Float(required=True, string="Precio Esperado")
    selling_price = fields.Float(readonly=True, copy=False, string="Precio de Venta")
    bedrooms = fields.Integer(default=2, string="Dormitorios")
    living_area = fields.Integer(string="Área Habitable sqm")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garaje")
    garden = fields.Boolean(string="Jardín")
    garden_area = fields.Integer(string="Área del Jardín sqm")
    garden_orientation = fields.Selection(
        [("north", "Norte"), ("south", "Sur"), ("east", "Este"), ("west", "Oeste")],
        string="Orientación del Jardín",
    )
    active = fields.Boolean(default=True, string="Activo")  # Reserved field
    state = fields.Selection(
        [
            ("new", "Nuevo"),
            ("offer_received", "Oferta recibida"),
            ("offer_accepted", "Oferta aceptada"),
            ("sold", "Vendido"),
            ("canceled", "Cancelado"),
        ],
        required=True,
        copy=False,
        default="new",
        string="Estado",
    )
    property_type_id = fields.Many2one("estate.property.type", string="Tipo de Propiedad")
    buyer_id = fields.Many2one("res.partner", copy=False, string="Comprador")
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user, string="Vendedor")
    tag_ids = fields.Many2many("estate.property.tag", string="Etiquetas")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Ofertas")
    total_area = fields.Integer(compute="_compute_total_area", string="Área Total")
    best_price = fields.Float(compute="_compute_best_price", string="Mejor Oferta")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        # pdb.set_trace()
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price")) if record.offer_ids else 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False
