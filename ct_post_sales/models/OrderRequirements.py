import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_

#------------------------------------------------------------------
#
#   Requerimientos de la Orden de Servicios
#
#------------------------------------------------------------------

class OrderRequirements (models.Model):
    _name="ct.post.sales.order.requirements"
    name=fields.Char("# Control")
    date=fields.Date('Fecha')
    note=fields.Text('Observaciones')


class OrderRequerimentsLine(models.Model):
    _name="ct.post.sales.order.requirements.line"
    qty=fields.Integer('Cantidad', default=1)



