import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class PartenerMigrate(models.Model):
    _name="ct.migrate.data.partner"
    rif=fields.Char('Ced/Rif', require=True)
    name=fields.Char('Razon', require=True)


