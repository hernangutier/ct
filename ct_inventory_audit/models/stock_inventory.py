import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Contenedor Logistico para administrar despacho de Pedidos
#
#--------------------------------------------------------------------

class StockInventory(models.Model):
    _inherit="stock.inventory"

    motivo=fields.Text('Motivo del Ajuste', required=True, default='S/I')
    #---- Falta Agregar Move Id de el Modulo de Auditorias
    audit_id = fields.Many2one(
        'ct.inventory.audit.case.audit',
        string='Caso de Auditoria',
        ondelete='restrict',
        index=True)