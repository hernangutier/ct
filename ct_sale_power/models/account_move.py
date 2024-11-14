import time
import math
import json
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


# --------------------------------------------------------------------
#
#  Modificacion a las Facturacion para Calculo de Comisiones
#
# --------------------------------------------------------------------

class AccountMove(models.Model):
    _inherit = "account.move"
    is_commissions_pay = fields.Boolean('Comision/Pagada', default=False, groups="ct_sale_power.ct_sale_power_group_user")
    status_pay_commission = fields.Selection([
        ('not_paid', 'No Pagada'),
        ('paid', 'Pagada'),
        ('calc', 'en Calculo'),
    ], string='Estado/Comision', copy=False, index=True, default='not_paid', store=True, required=True)
    amount_commission = fields.Float('Total/Comision', compute="_computed_amount_comission")
    date_last_payment = fields.Date('Fecha/Ult. Pago', compute="_get_last_payment_date")
    day_due_return = fields.Integer('Dias/Retraso', compute="_get_day_due_return")


    #--- Envia los Pagos  de la Factura
    def get_payments(self):
        for inv in self:

            list_ids = []
            js = json.loads(inv.invoice_payments_widget)

            if js:
                for pay in js['content']:
                    list_ids.append({
                        'id': pay['move_id']
                    })
                lines_ids = list(line['id'] for line in list_ids)
                payments = self.env['account.move'].browse(lines_ids).sorted(key=lambda x: x.date, reverse=True)
                return payments
            else:
                return None

    #---- Envia el Ultimo Pago de la Factura
    def _get_last_payment_date(self):
        for move in self:
            if move.get_payments() != None:
                for payments in move.get_payments():
                    move.date_last_payment = payments.date
                    break
            else:
                move.date_last_payment = False

    # ---- Cheka si existe un Pago en Efectivo no recibido
    def _check_payment_not_received(self):
        for inv in self:
            list_ids = []
            js = json.loads(inv.invoice_payments_widget)
            if js:
                response=True
                for pay in js['content']:
                    if pay['account_payment_id']:
                        #--- Consultamos en Pagos Ok...
                        payment_id=self.env['account.payment'].browse(int(pay['account_payment_id']))
                        if payment_id:
                            if payment_id.journal_id.type=='cash' and payment_id.is_disponible==False:
                                return False
        return response

    # --- Dias de Retraso en el Pago ---
    def _get_day_due_return(self):
        for i in self:
            if i.date_due_delivered:
                # Calculamos la Diferencia de dias Entre la fecha de el ultimo pago y la Fecha de Vencimiento segun despacho
                if i.date_last_payment:
                    diff = int((i.date_last_payment - i.date_due_delivered).days)
                    if diff < 0:
                        i.day_due_return = 0
                    else:
                        i.day_due_return = diff
                else:
                    i.day_due_return = 0
            else:
                i.day_due_return = 0

    #----- Returning Police Calculada segun las Reglas
    def get_police(self):
        police_rules = self.env['ct.sale.power.rules.police'].search([])
        percent = 0
        for p in police_rules:
            if self.day_due_return > p.lmin:
                percent = p.percent_police
        return percent

    #---- Computed los calculos de Comisiones ----
    def _computed_amount_comission(self):
        for i in self:
            amount_commission = 0
            for l in i.invoice_line_ids:
                amount_commission += l.amount_line_commission
            i.amount_commission = amount_commission

    #---- Metodo que Calcula la comision de la Factura ---
    def calculate(self):
        for l in self.invoice_line_ids:
            # ---- Calculamos la Linea de Comision
            if l.move_id.type == 'out_invoice':
                l.write({
                    'amount_line_commission': l.price_total * (l.product_id.percent / 100),
                    'percent_commission': l.product_id.percent
                })
            else:
                #---- Verificamos la Nota de Credito es un Cruce
                if l.move_id.type_note_credit=='cross':
                    l.write({
                        'amount_line_commission': -1 * l.price_total ,
                        'percent_commission': 100
                    })
                else:
                    l.write({
                        'amount_line_commission': -1 * l.price_total * (l.product_id.percent / 100),
                        'percent_commission': l.product_id.percent
                    })


    #---- Sobres escribimos los Metodos para actualizar

    def _check_is_commissions_calc(self):
        c=self.env['ct.sales.power.commissions.line'].search([
            ('account_id','=',self.id)
        ], limit=1)
        if len(c)>0:
            if c.move_id.state=='done' or c.move_id.state=='account':
                raise UserError('Este asiento contable fue relacionado para calculo de comisiones sobre Ventas!')
            else:
                raise UserError('Este asiento contable se encuentra en Calculo de comisiones sobre Ventas!')

    def button_draft(self):
        #--- Validamos la Factura ....
        self._check_is_commissions_calc()
        super(AccountMove, self).button_draft()



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    percent_commission = fields.Float('% de Comision', default=0)
    amount_line_commission = fields.Float('Monto de Comision', default=0)
