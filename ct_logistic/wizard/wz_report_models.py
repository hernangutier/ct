import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class ContainersCommons(models.TransientModel):
    _name="ct.logistic.containers.list.report.models"

    date_init=fields.Date('Desde', require=True)
    date_end=fields.Date('Hasta', require=True)
    all_route=fields.Boolean('Todas las Rutas', default=False)

    def getReport(self):
        pass



