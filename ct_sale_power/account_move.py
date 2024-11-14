import time
import math
import json
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Modificacion a las Facturacion para Calculo de Comisiones
#
#--------------------------------------------------------------------

class AccountMove(models.Model):
    _inherit="account.move"
    is_commissions_pay=fields.Boolean('Comision/Pagada', default=False)
    amount_commission=fields.Float('Total/Comision', compute="_computed_amount_comission")
    date_last_payment=fields.Date('Fecha/Ult. Pago', compute="_get_last_payment_date")


    def get_payments(self):
        js=json.loads(self.account_id.invoice_payments_widget)
        if js:
            for pay in js['content']:
                list_ids.append({
                    'id': pay['payment_id']
            })
        lines_ids=list(line['id'] for line in list_ids)
        payments= self.env['account.payment'].browse(lines_ids)
        payments=payments.sorted(key=lambda x: x.payment_date, reverse=True)
        return payments

    def _get_last_payment_date(self):
        for move in self:
            for payments in move.get_payments():
                move.date_last_payment=payments.payment_date
                break



    def _computed_amount_comission(self):
     for i in self:
        amount_commission=0
        for l in i.invoice_line_ids:
            amount_commission+=l.amount_line_commission
        i.amount_commission=amount_commission

    def calculate(self):
        for l in self.invoice_line_ids:
            #---- Calculamos la Linea de Comision
            l.write({
                'amount_line_commission': l.price_total*(l.product_id.percent/100),
                'percent_commission': l.product_id.percent
            })




class AccountMoveLine(models.Model):
    _inherit="account.move.line"
    percent_commission=fields.Float('% de Comision', default=0)
    amount_line_commission = fields.Float('Monto de Comision', default=0)







    