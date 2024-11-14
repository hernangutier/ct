import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzSaleOrderActionConfirm(models.TransientModel):
    _name="ct.logistic.sale.order.action.confirm"
    _description="Confirmacion de Pedidos"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Presupuest',
        ondelete='restrict',
        required=True,
        index=True)

