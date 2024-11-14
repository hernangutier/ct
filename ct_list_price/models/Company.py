import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Campos adicionales de forma para res.company agregamos footer y header
#
#--------------------------------------------------------------------

class ResCompany(models.Model):
    _inherit="res.company"

    img_list_price_header = fields.Binary(string="Lista de Precios Header", readonly=False)
    img_list_price_footer = fields.Binary(string="List de Precios Footer", readonly=False)
    img_card_product = fields.Binary(string="Card Producto", readonly=False)



