import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_

#------------------------------------------------------------------
#
#   Calculo de Comisiones segun Relaciones de Ordenes de Servicio
#
#------------------------------------------------------------------


class Commissions(models.Model):
    _name="ct.post.sales.commisions"
    date_close=fields.Date('Fecha de Corte', required=True)
    name=fields.Char('Ref', default="/")
    lines = []


    line_ids = fields.One2many('ct.post.sales.commissions.line', 'move_id', string='Ordenes de Servicio', copy=True,
                               readonly=True)

    amount=fields.Float('Total $', compute="_get_amount")


    # ---------- Estado de la Transaccion ---------------------
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('calc', 'en Calculo'),  # ---- Habiulitar Solicitudes de Repuestros
        ('rev', 'en Revision'),
        ('account', 'Contabilizado'),
    ], string='Estado', copy=False, index=True, default='new', store=True, required=True)

    #----- Calculos de Montos Totales
    def _get_amount(self):
        for l in self:
            amount = 0
            for lines in l.line_ids:
                amount+=lines.sub_amount
            l.amount=amount


    def action_calc(self):
        self.ensure_one()
        self.line_ids = [(5, 0, 0)]
        lines=[]
        os=self.env['ct.p.s.order.service'].search([
            ('state','=','done'),
            ('is_payment_comission','=',False)
        ])
        for rec in os:
          if str(rec.date_report_close) <=  str(self.date_close):
            vals = (0, 0, {
                'move_id': self.id,
                'os_id': rec.id,
            })
            lines.append(vals)
        if len(lines):
            self.write({
                'state': 'calc',
                'line_ids': lines
            })

        #---- Enviamos para la Vista de los Detalles de la Lineas
        self.action_view_os()

    @api.constrains('date_close')
    def _check_is_open(self):
        for l in self:
            count = l.search([
                ('state', '!=', 'account')
            ])
            if len(count) >= 1:
                raise ValidationError('Ya existe una transaccion en calculo')

    def action_view_os(self):
        self.ensure_one()
        domain = [('move_id', '=', self.id)]
        context={'create':0, 'delete': 0}
        action = {
            'name'          : _('Ordenes de Servicios'),
            'type'          : 'ir.actions.act_window',
            'view_mode'     : 'tree,form',
            'res_model'     : 'ct.post.sales.commissions.line',
            'domain'        : domain,
            'context'       : context
        }
        return action
    #--- Action View Invoices Supplier
    def action_view_invoice(self):
        pass

    def action_print_relations(self):
        self.ensure_one()
        raise UserError('Si')
    #--- Enviar a Revision
    def action_to_rev(self):
        self.ensure_one()
        self.write({
            'state' : 'rev'
        })

    #----- Contabilizar
    def action_to_account(self):
        self.ensure_one()
        self.write({
            'state' : 'account'
        })

    @api.model
    def create(self, vals):
        if "name" not in vals or vals["name"] == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('cos')
        commission = super(Commissions, self).create(vals)
        return commission


#------- Lineas de Calculos Relacionada con las Ordenes de Servicios -----
class CommissionsLine(models.Model):
    _name='ct.post.sales.commissions.line'

    #----- Relacion de Calculo de Comisiones por Centro de Servicio
    move_id = fields.Many2one('ct.post.sales.commisions', string='Relacion de Servicios',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
                              help="Movimiento de Entrada de la Linea")

    # ---- Orden de Servicio Asociada  ---
    os_id = fields.Many2one(
        'ct.p.s.order.service',
        string='Orden de Servicio',
        ondelete='restrict',
        required=True,
        index=True)

    def action_view_cost_tabulator(self):
        self.ensure_one()
        domain = [('order_id', '=', self.os_id.id)]
        contex={'create': 0, 'edit': 0, 'delete': 0}
        action = {
            'name'          : _('Costos Mano de Obra'),
            'type'          : 'ir.actions.act_window',
            'view_mode'     : 'tree',
            'res_model'     : 'ct.p.s.cost.tabulator.order.service',
            'domain'        : domain,
            'context'       : contex
        }
        return action

    exclude=fields.Boolean('Excluir del Calculo', help='Excluye la O.S. del calculo y la marcacomo pagada', default=False)
    #---- Datos Relacionados de las Ordenes de Servicio ---
    number = fields.Char('N# O.S.', related='os_id.name', store=True, readonly=False)
    partner_name = fields.Char('Distribuidor/Aliado', related='os_id.partner_id.name', store=True, readonly=False)
    service_name = fields.Char('Centro de Servicio', related='os_id.service_id.name', store=True, readonly=False)
    os_date_close = fields.Date('Fecha/Cierre', related='os_id.date_report_close', store=True, readonly=False)

    sub_amount = fields.Float('Sub-Total', related='os_id.amount_cost_tabulator', store=True, readonly=False)


