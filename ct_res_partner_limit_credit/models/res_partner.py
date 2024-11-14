import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------
# Campos adicionales para control de credito y restricciones
# en pedidos.....
#--------------------------------------------------------------


class Partner(models.Model):
    _inherit="res.partner"
    control_credit=fields.Boolean('Control de Credito', default=False)
    control_due = fields.Boolean('Controlar Saldos Vencidos', default=False)
    tolerance_day = fields.Integer('Dias de Tolerancia', default=1)
    type_constraing_sale = fields.Selection([
        ('sale', 'Restringir Reserva de Pedido'),
        ('invoice', 'Restringir Facturacion'),
    ], required=True, default='sale',
        help="Tipo de Restriccion a aplicar...")

    credit_disponible=fields.Float('Credito/Disponible', compute='_calculate_credit_disponible')


    def _calculate_credit_disponible(self):
        due_reserved=0
        if self.customer_due_amount<=0 :
            self.credit_disponible=self.credit_limit + self.customer_due_amount
        else:
            for s in self.sale_order_ids.filtered(lambda x: x.state=='sale' and x.invoice_status=='to invoice'):
                due_reserved+=s.amount_total
            #raise UserError(due_reserved)
            self.credit_disponible=self.credit_limit - (self.customer_due_amount + due_reserved)



    def invoice_due(self):
        invoice_due=self.env['account.move'].sudo().search(
            [('partner_id', '=', int(self.id)),
             ('state', '=', 'posted'),
             ('invoice_payment_state', '!=', 'paid'),
             ('date_due_delivered', '<', fields.Date.today())
             ])
        return invoice_due


