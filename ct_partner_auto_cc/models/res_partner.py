import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
#---------------------------------------------------------
#
#    Cambio al Modelo para autogenerar codigo comercial
#    al Customer ...... ok....
#---------------------------------------------------------

class ResPartner(models.Model):
    _inherit="res.partner"

    # ------- Reescritura de el Modelo de Datos -------------------
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('cc')
        partner = super(ResPartner, self).create(vals)
        return partner

    def write(self, vals):
        if 'ref' in vals:
            if not vals['ref']: vals['ref'] = self.env['ir.sequence'].next_by_code('cc')
        res = super(ResPartner, self).write(vals)
