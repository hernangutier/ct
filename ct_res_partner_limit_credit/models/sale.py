import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------
#  Restricciones y Alertas en los Pedidos
#
#--------------------------------------------------------------

class SaleOrder(models.Model):
    _inherit="sale.order"

    def do_notify(self,title,msj,type):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': msj,
                'type': type,  # types: success,warning,danger,info
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        return notification

    def invoice_due(self):
        if len(self.partner_id.invoice_due)>0:
            for i in self.partner_id.invoice_due:
                if i._get_day_due_return>self.partner_id.tolerance_day:
                    return true
                else:
                    return false


    def restrict_prepayment(self):
        self.ensure_one()
        conditions_lines=self.payment_term_id.line_ids.filtered(lambda x: x.days==0);
        if len(conditions_lines) >= 1:
            #---- Verificamos si Tiene Saldo a Favor a Facturar ---
            if  not self.partner_id.customer_due_amount<0:
                raise UserError(
                    'El Cliente: ' + self.partner_id.name + ' no tiene saldo a favor y esta en una condicion de PREPAGO... debe solicitar Pago!')
            else:
                if self.partner_id.customer_due_amount*-1 < self.amount_total:
                        raise UserError(
                            'El Cliente: ' + self.partner_id.name + ' no tiene saldo a favor y esta en una condicion de PREPAGO... debe solicitar Pago!')

    def check_rules(self):
        #---- Controlamos las Reglas de Control de redito ----
        if self.partner_id.control_credit:
            if self.partner_id.credit_limit == 0:
                return self.do_notify("Restriccion", "Limite de Credito no establecido!", 'danger')
            elif self.partner_id.credit_disponible < self.amount_total:
                return self.do_notify("Restriccion", "Credito disponible insuficiente!", 'danger')



    def check_rules_due(self,type):
        # --- Controlamos las Reglas de Saldos Venidos ----
        if self.partner_id.control_due:
            if type=='invoice':
               if self.partner_id.type_constraing_sale == 'invoice':
                    #--- Restringe la Facturacion por Ser Prepagado y no tener Pago...
                    self.restrict_prepayment()
                    # --- Restringe la Facturacion de Pedidos por Saldos
                    if self.partner_id.invoice_due():
                        raise UserError("Operacion no permitida por Saldo Vencido...")
            else:
                if self.partner_id.type_constraing_sale == 'sale':
                    # --- Restringe la Reserva y embalaje de Pedidos por Saldos
                    if self.partner_id.invoice_due():
                        raise UserError("Operacion no permitida por Saldo Vencido...")


    def action_confirm(self):
        self.check_rules()
        res = super(SaleOrder, self).action_confirm()
        return res