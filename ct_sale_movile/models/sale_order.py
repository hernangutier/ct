import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


# --------------------------------------------------------------------
#
#   Agregamos campo de referencia de Pedido Movil
#
# --------------------------------------------------------------------

class SaleOrder(models.Model):
    _inherit="sale.order"

    # ---- Referencia de el Pedido Movil --------
    sale_order_movile_id = fields.Many2one(
        'ct.sale.order.movile',
        string='Imagende Pedido',
        ondelete='restrict',
        index=True)

    require_fiscal = fields.Boolean('Solicita/Factura/Fiscal', default=False)
