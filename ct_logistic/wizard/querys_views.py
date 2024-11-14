import time
import matct
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class QSaleOrderDetail(models.TransientModels):
    _name="ctgl.logistic.qsaleorder.details"
    