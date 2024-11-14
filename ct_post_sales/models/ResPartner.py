import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_

#----------------------------------------------------------
#
#  Update ResPartner para Manejar Centros de Servicios
#
#----------------------------------------------------------
class ResPartner(models.Model):
    _inherit = ["res.partner"]
    is_centre_service=fields.Boolean('Es Centro de Servicio (S/N)', default=False)
    is_mechanical = fields.Boolean('Es Mecanico', default=False)

    def action_view_order_service_open(self):
        self.ensure_one()
        domain = [('service_id', '=', int(self.id)),('state','!=','')]

        action = {
            'name': _('Ordenes Abiertas'),
            'type': 'ir.actions.act_window',

            'view_mode': 'tree,form',
            'res_model': 'ct.p.s.order.service',
            'context': {'default_service_id': self.id,},
            'domain': domain,
        }
        return action