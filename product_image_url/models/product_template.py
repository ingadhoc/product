###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#   Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Nilmar Shereef(<https://www.cybrosys.com>)
#
#   This program is free software: you can modify
#   it under the terms of the GNU Affero General Public License (AGPL) as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
import base64
from urllib.request import urlopen
import requests
from PIL import Image
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    web_url = fields.Char(
        string='Image URL',
        help='Automatically sanitized HTML contents',
        copy=False,
    )

    @api.constrains('web_url')
    def onchange_image(self):
        for rec in self.filtered('web_url'):
            link = rec.web_url
            try:
                r = requests.get(link)
                Image.open(BytesIO(r.content))
                rec.image_medium = base64.encodestring(urlopen(link).read())
            except:
                raise ValidationError(
                    _("Please provide correct URL or check your image size.!"))
