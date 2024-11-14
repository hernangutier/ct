import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import json
#-----------------------------------------------------------
#
#      Modelo Payment Adaptado para Realizar control de efectivo
#
#-----------------------------------------------------------
class AccountPayment(models.Model):
    _inherit="account.payment"
    # ---- Control de Entrega de el Efectivo ----
    state_in = fields.Selection([
        ('new', 'Pendiente'),
        ('done', 'Enterado'),
    ], string='Estado/Entrega', copy=False, index=True, default='new', store=True, required=True)

    # --- Fecha de Entrega de el efectivo ----
    date_cash_in = fields.Date('Fecha/Entrega/Efectivo')


class efective_control(models.Model):
    _name="ct.cobranza.payment.efective.control"
    name=fields.Char('Ref', default='Nuevo')
    date=fields.Date('Fecha', required=True)
    amount=fields.Float('Total', compute="_calc", store=True)
    payment_count=fields.Integer("#Pagos", compute="_calc", store=True)
    #---- Pagos Registrados
    payment_ids = fields.Many2many(
        'account.payment',
        string='Pagos'
    )

    @api.depends('payment_ids')
    def _calc(self):
        for i in self:
            sum = 0
            count=0
            if i.payment_ids:
               for k in i.payment_ids:
                 sum+=k.amount
                 count+=1
        self.amount=sum
        self.payment_count=count

    #---- Estatus de la Operacion ----
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Procesado')
    ], string='Estado', copy=False, index=True, default='draft', store=True, required=True)

    note=fields.Text('Notas/Observaciones')

    def action_changed_draft(self):
        self.state='draft'

    #---- Metodo para Recalcular ----
    def action_calculate(self):
        self.payment_ids = [(5, 0, 0)]
        self.action_started()

    #---- Este Metodo Procesa la Transaccion y la cierra
    def action_post(self):
        for p in self.payment_ids:
            p.write({
                'state_in': 'done',
                'date_cash_in': self.date
            })
        self.state='done'

    #--- Este Metodo permite mostrar una  visat con los Pagos Realizados
    def action_view_payments(self):
        self.ensure_one()
        if self.payment_ids:
            domain = [('id', 'in', self.payment_ids.ids)]
            action = {
                'name': _('Pagos a Enterar'),
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref("ct_payment.view_jorven_payments_tree").id,
                'res_model': 'account.payment',
                'view_type': 'list',
                'view_mode': 'list',
                'context': {'edit': 0, 'create': 0, 'group_by': 'asesor_id'},
                'domain': domain,
            }
            return action
        else:
            raise UserError('No hay Pagos Cargados!')

    #---- Iniciar los Calculos
    def action_started(self):
        payments=self.env['account.payment'].search([
            ('state','not in', ('draft','cancelled')),
            ('is_disponible','=', True),
            ('state_in','=','new'),
            ('payment_type','=','inbound')
        ]).filtered(lambda x: x.journal_id.type=='cash')
        #---- Guardamos los ids de los Pagos en payments_ids
        self.write({
            'payment_ids': [(6,0,payments.ids)]
        })

    @api.model
    def create(self, vals):
        # self._check_lines_retrict(vals)
        if "name" not in vals or vals["name"] == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code('nce')
        payments = super(efective_control, self).create(vals)
        return payments