import time
import math
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class RecalculateDuePaymentTermDialog(models.TransientModel):
    _name="ct.cobranza.recalculate.due.payment.term.dialog"

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        required=True,
        index=True)

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Plazo/Pago',
        ondelete='restrict',
        required=True,
        index=True)

    def post(self):
        account=self.env['account.move'].search([('partner_id','=',self.partner_id.id)])
        line=""
        for line in self.payment_term_id.line_ids:
            if line:
                break
        for acc in account:
           try:
            if acc.state=='posted':
                if acc.date_delivered:
                    acc.write({
                        'invoice_payment_term_id': self.payment_term_id.id,
                        'date_due_delivered': acc.recalculate_due_for_int_days(acc.date_delivered,line.days)
                    })
                else:
                    acc.write({
                        'invoice_payment_term_id': self.payment_term_id.id,
                        'invoice_date_due': acc.recalculate_due_for_int_days(acc.invoice_date, line.days)
                    })
           except Exception as e:
               raise UserError(str(e))


class SaldosProyectadosDialog(models.TransientModel):
    _name="ct.cobranza.saldos.proyectados.dialog"

    date_end=fields.Date('Fecha de Proyeccion', required=True)

    def get_view(self):
        self.ensure_one()
        domain = [('date_due_delivered', '<=', datetime.datetime.strptime(str(self.date_end), '%Y-%m-%d').date()),('type','=','out_invoice'),('state','=','posted'),('invoice_payment_state','=','not_paid')]
        action = {
            'name': _('Cuentas por Cobrar Proyeccion'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_id': self.env.ref("ct_cobranza.view_ct_cobranza_account_move_due_delivered_tree").id,
            'context': {'edit': 1, 'create': 0},
            'view_type': 'list',
            'view_mode': 'list',
            'domain': domain,
        }
        return action




