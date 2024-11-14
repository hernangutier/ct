import time
import datetime
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

# ----------------------------------------------------------
#
#    Modelo Para Gestionar Dialog de para Impresion de Notas de Entregas
#    Facturas y Picking de Despacho
#
#
# ----------------------------------------------------------

class dialogReport(models.TransientModel):
    _name="ct.note.account.report.dialog.form"

    # ----- Tipo de Container ----------
    type = fields.Selection([
        ('note', 'Nota de Entrega'),
        ('account', 'Factura'),
        ('picking', 'Picking')
    ], string='Tipo Documento', copy=False, index=True, default='note', required=True)

    #------ Identificador para Nota de entrega ---
    account_move_id = fields.Many2one(
        'account.move',
        string='Nota/Entrega',
        ondelete='restrict',
        index=True)

    # ------ Identificador para Picking ---
    stock_picking_id = fields.Many2one(
        'stock.picking',
        string='Picking(Movimiento de Inventario)',
        ondelete='restrict',
        index=True)






    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'id': self.account_move_id.id,
                'picking_id': self.stock_picking_id.id,
            },
        }
        if self.type=='note':
            return self.env.ref('ct_note_account_report.action_account_move_note_report_pdf').report_action(self, data=data)
        else:
            return self.env.ref('ct_note_account_report.action_stock_picking_report_pdf').report_action(self,
                                                                                                            data=data)

class ReportNote(models.AbstractModel):
    _name="report.ct_note_account_report.ct_report_600"

    def _get_report_values(self, docids, data=None):
            model= self.env['account.move'].browse(int(data['form']['id']))

            return {
                'doc_ids': model.id,
                'doc_model': data['model'],
                'date_publish': time.strftime('%Y-%m-%d'),
                'company': self.env.user.company_id,
                'user': self.env.user,
                'docs': model,

            }

class ReportPicking(models.AbstractModel):
    _name="report.ct_note_account_report.ct_report_602"

    def _get_report_values(self, docids, data=None):
            model= self.env['stock.picking'].browse(int(data['form']['picking_id']))

            return {
                'doc_ids': model.id,
                'doc_model': data['model'],
                'date_publish': time.strftime('%Y-%m-%d'),
                'company': self.env.user.company_id,
                'user': self.env.user,
                'docs': model,

            }



