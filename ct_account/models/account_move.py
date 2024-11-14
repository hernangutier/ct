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
