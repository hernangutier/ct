import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Adecuacion de la Facturacion para control Logistico
#
#--------------------------------------------------------------------


class ResPartner(models.Model):
    _inherit="res.partner"

    delivery_proposal = fields.Selection([
        ('ddt', 'DDT'),
        ('glp', 'en Empresa'),
        ('enc', 'Encomienda')
    ], string='Sugerencia de Envio', copy=False, index=True, default='ddt', store=True, required=True)


    recovery_expenses = fields.Float('% Gastos de Recuperacion', default=0.0)

    is_rrhh_transport=fields.Boolean('Es Personal/Trasporte', default=False)

    supplier_service = fields.Boolean('Presta Servicio de Transporte', default=False)

    street_delivered=fields.Text('Direccion/Despacho', default="N/A", required=True)
