import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class WzPickingUpdatePacking(models.TransientModel):
    _inherit="ct.sale.management.picking.action.form.post"

    def action_post(self):
        if self.packing_register<=0:
            raise UserError('Debe ingresar el Numero de Bultos!')
        sale_order=self.env['sale.order'].serach([('name','=',self.sale_order_id.origin)])
        if sale_order:
            sale_order.write({
                'packing_register': self.packing_register
            })
        else:
            raise UserError('Este Picking no es de un Pedido para actualizar Bultajes...')
