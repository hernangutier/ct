import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzEfectiveReportForm(models.TransientModel):
    _inherit="ct.commons.wz.commons"
    _name="ct.payment.wz.efective.report.form"
    _description="Registro de Pagos en Efectivo"

    disponible=fields.Boolean('Disponible', default=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_init': str(self.date_init),
                'date_end': str(self.date_end),
                'disponible': 1 if self.disponible else 0,
                'title': "Pagos Registrados Disponibles" if self.disponible else "Pagos Registrados No Disponibles",
            },
        }
        return self.env.ref('ct_payment.payment_efective_report_400').report_action(self, data=data)

class ReportEfective(models.AbstractModel):
    _name = "report.ct_payment.ct_pdf_report_400"

    def _get_report_values(self, docids, data=None):
        date_init=data['form']['date_init']
        date_end=data['form']['date_end']
        ids=self.env['account.journal'].search([('type','=','cash')])
        docs = self.env['account.payment'].search_read([
            '&', ('payment_date', '>=',date_init ), ('payment_date', '<=', date_end),
            ('payment_type','=','inbound'),
            ('partner_type','=','customer'),
            ('is_disponible','=', int(data['form']['disponible'])),
            ('journal_id', 'in', ids.ids),
        ],order='payment_date asc')
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_init': data['form']['date_init'],
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'docs': docs,
            'disponible': data['form']['disponible'],
            'title': data['form']['title']
        }

