import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzAddDiscount(models.TransientModel):
    _name="ct.sale.management.dialog.add.discount.form"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido#',
        ondelete='restrict',
        require=True,
        index=True)

    discount=fields.Float('% Descuento a aplicar', default=0, required=True)


    def post(self):
        invoices=self.sale_order_id.invoice_ids.filtered(lambda x: x.state=='posted')
        if len(invoices)>0:
            raise UserError('Este pedido ya tiene Movimientos Contables debe proceder por Notas de Credito...')

        if self.sale_order_id:
            for l in self.sale_order_id.order_line:
                l.write({
                    'discount': self.discount
                })
        return self.sale_order_id
