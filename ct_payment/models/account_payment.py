import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import json
#-----------------------------------------------------------
#
#      Agregamos campo que calcula dias de Vencimiento de la
#      Factura
#-----------------------------------------------------------

class AccountPayment(models.Model):
    _inherit="account.payment"
    number=fields.Char('Control #')
    is_disponible=fields.Boolean("Efectivo/Disponible", default=False)
    note=fields.Text('Observaciones')





