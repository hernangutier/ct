import time
import datetime
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzDueByUser(models.TransientModel):
    _name="ct.due.by.asesor.form"

    # --------- Ruta Sugerida --------
    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        require=True,
        index=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        require=True,
        index=True)

    type = fields.Selection([
        ('gen', 'General'),
        ('by_user', 'Por Asesor'),
        ('by_client', 'Por Cliente'),
    ], string="Tipo/Reporte", default='gen')

    date=fields.Date(string='Fecha/Corte', required=True)

    def get_report(self):
         data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'type': str(self.type),
                'user_id': self.user_id.id if self.user_id.id else None,
                'partner_id': self.partner_id.id if self.partner_id.id else None,
                'date_end': self.date,
                'title': "Saldos Vencidos por Asesor"
            },
         }
         if self.type=='by_user':
             return self.env.ref('ct_cobranza.ct_cobranza_report_1005').report_action(self, data=data)
         if self.type=='by_client':
             return self.env.ref('ct_cobranza.ct_cobranza_report_1006').report_action(self, data=data)
         if self.type == 'gen':
             return self.env.ref('ct_cobranza.ct_cobranza_report_1007').report_action(self, data=data)



class WzDueByUserReport(models.AbstractModel):
    _name = "report.ct_cobranza.ct_pdf_report_1005"

    def _get_report_values(self, docids, data=None):
        partner_data=[]
        #----- Consultamos las Facturas Pendientes
        invoices=self.env['account.move'].search([
            ('user_id','=',int(data['form']['user_id'])),
            ('state','=','posted'),
            ('type','=','out_invoice'),
            ('state_delivered', '=', True),
            ('date_due_delivered', '<=', datetime.datetime.strptime(str(data['form']['date_end']), '%Y-%m-%d').date()),
            ('invoice_payment_state','=','not_paid')
        ])
        #Consultamos el Grupo de la Cabecera ---
        group_partner = self.env['account.move'].with_context(orderby="partner_id.name ASC").read_group(
            [
                ('user_id', '=', int(data['form']['user_id'])),
                ('state', '=', 'posted'),
                ('type', '=', 'out_invoice'),
                ('state_delivered', '=', True),
                ('date_due_delivered', '<=', datetime.datetime.strptime(str(data['form']['date_end']), '%Y-%m-%d').date()),
                ('invoice_payment_state', '=', 'not_paid')
            ],
            ['partner_id', 'partner_id.name'],
            ['partner_id'],

        )
        #--- Creamos el Array de el Grupo
        for l in group_partner:
            partner = self.env['res.partner'].browse(int(l.get('partner_id')[0]))
            partner_data.append({
                'id': partner.id,
                'name': partner.name,
                'count': l.get('partner_id_count')
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'asesor': self.env['res.users'].browse(int(data['form']['user_id'])).name,
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'header': partner_data,
            'lines': invoices
        }


class WzDueByClientReport(models.AbstractModel):
    _name = "report.ct_cobranza.ct_pdf_report_1006"

    def _get_report_values(self, docids, data=None):

        #----- Consultamos las Facturas Pendientes
        invoices=self.env['account.move'].search([
            ('partner_id','=',int(data['form']['partner_id'])),
            ('state','=','posted'),
            ('type','=','out_invoice'),
            ('state_delivered', '=', True),
            ('date_due_delivered', '<=', datetime.datetime.strptime(str(data['form']['date_end']), '%Y-%m-%d').date()),
            ('invoice_payment_state','=','not_paid')
        ])


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'partner_name': self.env['res.partner'].browse(int(data['form']['partner_id'])).name,
            'partner_id': int(data['form']['partner_id']),
            'lines': invoices
        }


class WzDueGeneralReport(models.AbstractModel):
    _name = "report.ct_cobranza.ct_pdf_report_1007"

    def _get_report_values(self, docids, data=None):
        partner_data=[]
        #----- Consultamos las Facturas Pendientes
        invoices=self.env['account.move'].search([
            ('state','=','posted'),
            ('type','=','out_invoice'),
            ('state_delivered', '=', True),
            ('date_due_delivered', '<=', datetime.datetime.strptime(str(data['form']['date_end']), '%Y-%m-%d').date()),
            ('invoice_payment_state','=','not_paid')
        ])
        #Consultamos el Grupo de la Cabecera ---
        group_partner = self.env['account.move'].with_context(orderby="partner_id.name ASC").read_group(
            [
                ('state', '=', 'posted'),
                ('type', '=', 'out_invoice'),
                ('state_delivered', '=', True),
                ('date_due_delivered', '<=', datetime.datetime.strptime(str(data['form']['date_end']), '%Y-%m-%d').date()),
                ('invoice_payment_state', '=', 'not_paid')
            ],
            ['partner_id', 'partner_id.name'],
            ['partner_id'],

        )
        #--- Creamos el Array de el Grupo
        for l in group_partner:
            partner = self.env['res.partner'].browse(int(l.get('partner_id')[0]))
            partner_data.append({
                'id': partner.id,
                'name': partner.name,
                'count': l.get('partner_id_count')
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'header': partner_data,
            'lines': invoices
        }



