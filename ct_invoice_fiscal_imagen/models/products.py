import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Imagen de Factura Fiscal
#
#--------------------------------------------------------------------

class Product(models.Model):
      _inherit="product.template"
      is_exent=fields.Boolean('Es Exento',defaul=False)

