import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Campos adicionales de forma para product.template
#
#--------------------------------------------------------------------

class AccountMove(models.Model):
    _inherit="account.move"

    #------ Type para Notas de Credito Aplicar Descuento post  Facturacion
    type_note_credit = fields.Selection([
        ('desc', 'Descuento'),
        ('dev', 'Devolucion'),
        ('cross', 'Cruce/Cuenta'),
    ], string='Tipo Nota/Credito', copy=False, index=True, default='dev', store=True, required=True)


    is_due=fields.Boolean('Factura Vencida',compute="_compute_invoice_due")

    is_file_admin = fields.Boolean('Documento en Archivo (S/N', default=False)

    def _compute_invoice_due(self):
      for inv in self:
        if inv.invoice_date_due < fields.Date.from_string(time.strftime('%Y-%m-%d')):
            inv.is_due=True
        else:
            inv.is_due=False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.user_id:
            self.invoice_user_id = self.partner_id.user_id


    def action_view_note_credit_special(self):
        return {
            'name': _('Generar Nota/Credito/Especial'),
            'context': {'active_id': self.id},
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ct.account.note.credit.special.dailog.form',
            'view_id': self.env.ref("ct_account.ct_account_note_credit_special_dialog").id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class AccountMoveFile(models.Model):
    _name= "ct.account.account.move.file"

    name = fields.Char('Referencia:', default="/")

    date=fields.Date('Fecha', default=fields.Date.today())

    user_send = fields.Many2one(
        'res.users',
        string='Envia',
        ondelete='restrict',
        required=True,
        index=True)

    user_receive = fields.Many2one(
        'res.users',
        string='Recibe',
        ondelete='restrict',
        required=True,
        index=True)


    state = fields.Selection([
        ('new', 'Nuevo'),
        ('done', 'Procesado'),
    ], string='Estado', copy=False, index=True, default='new', store=True, required=True)



    note = fields.Text('Notas:', default=" ")


    documents_ids = fields.Many2many(
        'account.move',
        string='Documentos',
        domain = [('state', '=', 'posted'),
                  ('is_file_admin', '=', False)],
    )

    documents_counter=fields.Integer('count', compute="_get_count_doc", store=True)

    #----- Funcion Multi para Calcular el Nomero de Documentos cargados
    def _get_count_docs(self):
        for l in self:
            l.document_counter=len(l.document_ids)

    #----- AAction Post
    def action_post(self):
        for l in self.documents_ids:
            l.write({
                'is_file_admin': True
            })
        self.state='done'
        return self