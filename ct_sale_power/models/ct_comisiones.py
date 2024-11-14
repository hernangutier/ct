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
#  Modelo de Calculo de Comisiones Sobre Ventas Rev: 8-5-2024
#
# --------------------------------------------------------------------

class Commisions(models.Model):
    _name = "ct.sale.power.commissions"
    name = fields.Char('Ref')
    concept = fields.Text('Concepto o Descripcion', required=True)
    date_end = fields.Date('Fecha de Corte', required=True)
    #---- Asesor de Ventas ---
    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        required=True,
        index=True)
    #---- Status de la Comision
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('calc', 'en Calculo'),
        ('rev', 'en Revision'),
        ('done', 'Procesado'),
        ('account', 'Contabilizado')
    ], string='Estado', copy=False, index=True, default='new', store=True, required=True)
    # ---- Calculos Totales ---
    amount_total = fields.Float('Monto Calculado', compute="_compute_amount")
    amount_police = fields.Float('Monto Penalizado', compute="_compute_amount")
    amount_adjust_total = fields.Float('Monto Ajustado', compute="_compute_amount")
    amount_restrict = fields.Float('Monto Penalizado')
    amount_add = fields.Float('Asignaciones/Especiales',compute="_compute_amount")
    amount_negative = fields.Float('Deducciones',compute="_compute_amount")
    line_ids = fields.One2many('ct.sales.power.commissions.line', 'move_id', string='Facturas/Notas Credito', copy=True,
                               readonly=True)

    # ----- Depends Lines_ids Computed
    @api.depends('line_ids')
    def _compute_amount(self):
        for c in self:
            total = 0.0
            ajust = 0.0
            asig=0.0
            deduc=0.0

            for l in c.line_ids:
                total += l.amount_commission
                ajust += l.amount_commission_adjust
            for l1 in self.env['ct.sale.power.ad.efect'].search([('move_id','=',c.id)]):
                if l1.type=='asig':
                    asig+=l1.amount
                else:
                    deduc += l1.amount

            # --- Actualizamos las Lineas
            c.amount_add=asig
            c.amount_negative=deduc
            c.amount_total = total
            c.amount_adjust_total = ajust+c.amount_add-c.amount_negative
            c.amount_police = total - ajust

    #----- Metodo para Reabrir los Calculos de Comisiones
    def re_open(self):
        if self.state=='done':
            raise UserError('No se puede abrir el Calculo porque ya se encuentra Procesado...')
        for line in  self.line_ids:
            line.account_id.write({
                'is_commissions_pay': False
            })
        self.write({
            'state': 'calc'
        })

    #---- Metodo para Enviar los calculos a Revision
    def send_rev(self):
      if len(self.line_ids)==0 :
         raise UserError('No existen Facturas a Revisar...')
      if self.amount_adjust_total<=0:
         raise UserError('No existe monto valido a Revisar...')
      self.state='rev'


    #---- Este Metodo Inicia el Calculo con en Calculo inicial y cambia de Estado
    def started(self):
        self.calc()
        if len(self.line_ids)>0:
            self.state="calc"
        else:
            raise UserError('No hay facturas a Cacular...')

    #---- Este Metodo Realiza los Calculos de Comisiones Action Recalcular
    def calc(self):
        lines = []
        self.line_ids = [(5, 0, 0)]
        invoices = self.env['account.move'].search([
            ('invoice_user_id', '=', self.user_id.id),
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
            ('invoice_payment_state', '=', 'paid'),
            ('is_commissions_pay', '=', False)
        ])

        for i in invoices:
            #---- Checamos si existe algun Pago en Efectivo que no este Recibido para omitir la Factua en el Calculo
            if  i._check_payment_not_received():
              if i.date_last_payment<=self.date_end:
                    # --- Calulamos las Comisones sobre Lineas
                    i.calculate()
                    percent_police=0
                    #---- Aplicar Aqui Penalizacion ---
                    percent_police=i.get_police()

                    vals = (0, 0, {
                        'account_id': i.id,
                        'percent_police': percent_police
                    })
                    lines.append(vals)

        self.write({
            'line_ids': lines
        })

    #----- Metodo para Reabrir los Calculos de Comisiones
    def open_calc(self):
        self.state="calc"

    #--- Metodo para Aprobar las Comisiones
    def post(self):
        for i in self:
            i.state='done'
            for l in i.line_ids:
                l.account_id.write({
                    'is_commissions_pay': True
                })

    #--- Metodo para Contabilizar Comisiones sobre Ventas
    def action_account(self):
        #--- Restricciones o Validaciones -----
        if self.amount_adjust_total<=0:
            raise UserError('No se puede contabilizar este Monto Calculado....')
        #--- Creamos la Factura de Cuenta por Pagar al Asesor de Ventas
        line = []
        invoice= self.env['account.move']
        i=invoice.create({
                'ref': 'Comisiones/Ventas #: ' + str(self.name),
                'invoice_payment_ref': self.name,
                'invoice_origin': self.name,
                'type': 'in_invoice',
                'partner_id': self.user_id.partner_id.id,
                'journal_id': 11,
            }
        )
        #---- Creamos la Linea de Facturacion ....
        vals = (0, 0, {
            'product_id': self.env['product.product'].search([('default_code', '=', '004247')], limit=1).id,
            'name': 'Asesoramiento en Ventas de Productos Ferreteros al Corte ' + str(self.date_end),
            'quantity': 1,
            'price_unit': self.amount_adjust_total
        })
        line.append(vals)
        i.write({
            'invoice_user_id': self.user_id.id,
            'invoice_line_ids': line
        })
        i.action_post()
        #---- Actualizamos el Estado de la Transaccion ---
        self.state="account"



    # --- Metodo llamar la Vista de los Documentos implicados
    def action_view_related_account_move_loads(self):
        self.ensure_one()
        if self.line_ids:
            domain = [('move_id', '=', self.id)]
            action = {
                'name': _('Facturas Cargadas'),
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref("ct_sale_power.view_account_move_lines_loads_tree").id,
                'res_model': 'ct.sales.power.commissions.line',
                'view_type': 'list',
                'view_mode': 'list',
                'context': {'edit': 1, 'create': 0},
                'domain': domain,
            }
            return action
        else:
            raise UserError('No hay Documentos Cargados!')
    #--- Metodo para llamar a Vista de Facturas Cuentas por Pagar a Asesores
    def action_view_related_accout_move_suppl(self):
        self.ensure_one()

        domain = [('invoice_origin', '=', self.name)]
        action = {
                'name': _('Cuentas X Pagar'),
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref("account.view_invoice_tree").id,
                'res_model': 'account.move',
                'view_type': 'list',
                'view_mode': 'list',
                'context': {'edit': 1, 'create': 0},
                'domain': domain,
        }
        return action

    # --- Metodo para llamar a Vista de Asignaciones y Deducciones
    def action_view_related_efects(self):
        self.ensure_one()

        domain = [('move_id', '=', self.id)]
        action = {
            'name': _('Asignaciones/Deducciones'),
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref("ct_sale_power.view_related_efects_tree").id,
            'res_model': 'ct.sale.power.ad.efect',
            'view_type': 'list',
            'view_mode': 'list',
            'context': {'default_move_id': self.id},
            'domain': domain,
        }
        return action

    @api.constrains('user_id')
    def restrict(self):
      #for rec in self:
        self.ensure_one()
        id=self.env['ct.sale.power.commissions'].search([
            ('user_id','=',self.user_id.id),
            ('id','!=',self._origin.id),
            ('state','in',('new','calc','rev','done'))
        ])
        if len(id)>0:
            raise UserError(len(id))



    #------ Metodo Create con algunas modificaciones y Validaciones
    @api.model
    def create(self, vals):
            #self.restrict()
            if "name" not in vals or vals["name"] == "new":
                vals['name'] = self.env['ir.sequence'].next_by_code('cv')
            commissions = super(Commisions, self).create(vals)
            return commissions


# ---- Modelo de Lineas de Facturas Afectadas en Comisiones
class CommissionsLines(models.Model):
    _name = "ct.sales.power.commissions.line"

    move_id = fields.Many2one('ct.sale.power.commissions', string='Calculo',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
                              help="Movimiento de Entrada de la Linea")
    # ---- Factura Asociada ---
    account_id = fields.Many2one(
        'account.move',
        string='Factura/Nota Credito',
        ondelete='restrict',
        required=True,
        index=True)
    # ---- Datos de la Factura ---
    company_id = fields.Many2one(related='account_id.company_id', store=True, readonly=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                          readonly=True, store=True,
                                          help='Utility field to express amount currency')
    number = fields.Char('N# Doc.', related='account_id.name', store=True, readonly=False)
    partner_name = fields.Char('Cliente', related='account_id.partner_id.name', store=True, readonly=False)
    date_move = fields.Date('Emision', related='account_id.invoice_date', store=True, readonly=False)
    date_delivered = fields.Date('Despacho', related='account_id.date_delivered', store=True, readonly=False)
    date_due_delivered = fields.Date('Vencimiento/Despacho', related='account_id.date_due_delivered', store=True, readonly=False)
    amount_total_signed=fields.Monetary('Monto', related='account_id.amount_total_signed', store=True, readonly=False, currency_field='company_currency_id')
    amount_commission=fields.Float('Comision/Calculada', related='account_id.amount_commission', readonly=False)
    percent_police=fields.Float('% Penalizacion', default=0)
    amount_commission_adjust=fields.Float('Comision/Ajustada', compute="_cal_commission_adjust")
    representative_percentage=fields.Float("% Representativo", compute="_calc_related")
    ref = fields.Char('Memo', related="account_id.ref")
    invoice_payment_term_desc = fields.Char('Plazo/Pago', related='account_id.invoice_payment_term_id.name', readonly=True)
    date_last_payment=fields.Date('Fecha/Ult. Pago', related='account_id.date_last_payment', readonly=False)
    day_due_return=fields.Integer('Dias/Retraso', related='account_id.day_due_return', store=True, readonly=False)
    type_doc=fields.Char("Tipo/Doc", help="Tipo de Documento FV: Factura de Ventas NC: Nota de Credito",compute="_calc_related")
    # ----- Porcentaje Representativo
    def _calc_related(self):
        for i in self:
            i.representative_percentage = round((i.amount_commission * 100) / i.amount_total_signed, 2)
            if i.account_id.type=='out_invoice': i.type_doc='FV'
            if i.account_id.type == 'out_refund': i.type_doc = 'NC'

    @api.constrains('percent_police')
    def restricLineInvoice(self):
        for rec in self:
            if rec.move_id.state in ('rev','done','account'):
                raise UserError('No puede editar la linea porque el Calculo esta Cerrado...')

    @api.depends('percent_police')
    def _cal_commission_adjust(self):
        for l in self:
            if l.percent_police<0 or l.percent_police>100 : raise UserError('Porcentaje de Penalizacion debe estar en 0-100%')

            if l.percent_police>0:
                l.amount_commission_adjust=l.amount_commission*((100-l.percent_police)/100)
            else:
                l.amount_commission_adjust=l.amount_commission


    def unlink(self):
        for rec in self:
            if self.env['ct.sales.power.commissions.line'].browse(rec.id).move_id.state in (
                'rev', 'done', 'account'):
                    raise UserError('No se puede eliminar una Factura si no esta en Calculo...')
        return super(CommissionsLines,self).unlink()


#--------- Asignaciones y Deducciones Foraneas
class Efects(models.Model):
    _name="ct.sale.power.ad.efect"
    ref=fields.Char('Referencia', default='/')
    move_id = fields.Many2one('ct.sale.power.commissions', string='Calculo',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
                              help="Movimiento de Entrada de la Linea")

    type = fields.Selection([
        ('asig', 'Asignacion'),
        ('deduc', 'Deduccion'),
    ], string='Estado', copy=False, index=True, default='asig', store=True, required=True)

    name=fields.Char('Descripcion')
    amount=fields.Float('Monto $', default=1)

    #--- Metodo Create
    @api.constrains('name','type','amount')
    def restrict(self):
        for rec in self:
            id = self.env['ct.sale.power.ad.efect'].search([
                ('move_id', '=', rec.move_id.id)
            ])
            filter=id.filtered(lambda x: x.move_id.state not in ('calc'))
            if len(filter) > 0:
                raise UserError(
                    'No se puede agregar o editar Asignaciones/Deducciones porque no esta en Calculo...')

    def unlink(self):
        for rec in self:
            if self.env['ct.sale.power.ad.efect'].browse(rec.id).move_id.state in (
                'calc'):
                    raise UserError('No se puede eliminar una Asignacion/Deduccion si no esta en Calculo...')
        return super(Efects,self).unlink()

    @api.model
    def create(self, vals):
        # self.restrict()
        if "ref" not in vals or vals["ref"] == "/":
            if vals['type']=='asig':
                vals['ref'] = self.env['ir.sequence'].next_by_code('add')
            else:
                vals['ref'] = self.env['ir.sequence'].next_by_code('deduc')
        efect = super(Efects, self).create(vals)
        return efect