import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class DialogNoteCredit(models.TransientModel):
    _name="ct.account.note.credit.special.dailog.form"
    #--- Fcatura a Afectar en la Nota de Credito
    account_id = fields.Many2one(
        'account.move',
        string='Factura/Afectar',
        ondelete='restrict',
        index=True)

    type_note_credit = fields.Selection([
        ('desc', 'Descuento'),
        ('cross', 'Cruce/Cuenta'),
    ], string='Tipo Nota/Credito', copy=False, index=True, default='desc', store=True, required=True)
    amount=fields.Float('Monto', required=True, compute="_ondepends_values")
    percent=fields.Float('% Porcentaje', default=5.0)


    @api.onchange('type_note_credit','percent')
    def _ondepends_values(self):
        if self.type_note_credit=='desc':
           if self.percent>0:
              self.amount=self.account_id.amount_total-self.account_id.amount_total*((100-self.percent)/100)
           else:
               self.percent=5
               self.type_note_credit=='desc'
               raise UserError('Porcentaje no valido!')
        else:
           if self.account_id.amount_residual==0:
               self.amount=0
               raise UserError('Esta Asiento no posee saldo...')
           else:
               self.amount=self.account_id.amount_residual
    #--- Metodo para Procesar las Notas de Credito Especiales ---
    def action_post(self):
        #--- Restricciones ----
        if self.amount==0:
            raise UserError('Monto a Registrar No Valido!')
        #---- Creamos la Nota de Credito ---
        note_credit=self.account_id._reverse_moves()
        note_credit.type_note_credit==self.type_note_credit
        #--- Eliminamos las Lineas
        note_credit.invoice_line_ids=[(5, 0, 0)]
        ref=""
        if self.type_note_credit=='desc':
            vals = (0, 0, {
                'product_id': self.env['product.product'].search([('default_code','=','12-000102')],limit=1).id,
                'name': 'Descuento ' + str(self.percent) + '% sobre la factura ' + self.account_id.name + ' por un monto de ' + str(self.account_id.amount_total),
                'quantity': 1,
                'price_unit': self.amount
            })
            ref='Descuento ' + str(self.percent) + '% sobre la factura ' + self.account_id.name + ' por un monto de ' + str(self.account_id.amount_total)
        else:
            vals = (0, 0, {
                'product_id': self.env['product.product'].search([('default_code','=','004247')],limit=1).id,
                'name': 'Saldo Restante sobre la factura ' + self.account_id.name + ' imputado al asesor para cierre de factura...',
                'quantity': 1,
                'price_unit': self.amount
            })
            ref='Saldo Restante sobre la factura ' + self.account_id.name + ' imputado al asesor para cierre de factura...'
        #----- Preparcion de la Linea de Factura Unica
        line=[]
        line.append(vals)
        #---- Actualizamos la Nota de Credito
        note_credit.write({
            'ref': ref,
            'type_note_credit': self.type_note_credit,
            'invoice_user_id': self.account_id.invoice_user_id.id,
            'invoice_line_ids': line
        })
        #--- Publicamos la Nota de Credito ---
        note_credit.action_post()
        #--- Retornar la Vista de la Factura ---
        return note_credit



