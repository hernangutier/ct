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

    @api.constrains('amount')
    def check_amount(self):
        if self.amount<=0:
            raise UserError('Debe suministrar un Importe Valido!')


    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        required=True,
        index=True)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.user_id:
            self.asesor_id=self.partner_id.user_id










