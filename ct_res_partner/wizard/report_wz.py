import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Listados de Clientes
#
#--------------------------------------------------------------------

class WzPartnerListPdf(models.TransientModel):
    _inherit="ct.commons.wz.commons"
    _name="ct.res.partner.list.pdf.wz"

    # --------- Estado de Preparacion de Pedido  --------
    type_class = fields.Selection([
        ('user', 'por Asesor/Ventas'),
        ('team', 'por Zona/Ventas'),
        ('state', 'por Estado'),
        ('pay', 'por Plazos de Pago'),

    ], string="Clasificacion/Agrupacion", default='user')

    #----- Todos a Solo Uno  --------
    type_mod = fields.Boolean('General/Selectivo', default=True)


    #---- Para Consultar por Asesor de Ventas
    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Zona de Ventas
    zone_id = fields.Many2one(
        'crm.team',
        string='Zona/Ventas',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Estado
    country_id = fields.Many2one(
        'res.country',
        string='Estado',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Plazos de Pago
    payment_term_id=fields.Many2one(
        'account.payment.term',
        string='Plazos de Pago',
        ondelete='restrict',
        index=True)

    def get_report(self):
        pass


