import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Listados de Clientes por Limite de Credito
#
#--------------------------------------------------------------------

class WzPartnerListLimitPdf(models.TransientModel):
    _inherit="ct.commons.wz.commons"
    _name="ct.res.partner.list.limit.pdf.wz"



