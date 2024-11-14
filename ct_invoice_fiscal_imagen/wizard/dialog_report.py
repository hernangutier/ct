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
#    Modelo Para Gestionar Dialog de para Impresion de Facturas Fiscales
#
#
#
# ----------------------------------------------------------

class dialogReport(models.TransientModel):
    _name="ct.invoice.fiscal.imagen.dialog.form"


    #------ Identificador para Nota de entrega ---
    image_id = fields.Many2one(
        'ct.invoice.fiscal.imagen',
        string='Factura/Fiscal',
        ondelete='restrict',
        index=True)





    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'id': self.image_id.id,
            }
        }
        return self.env.ref('ct_invoice_fiscal_imagen.action_invoice_fiscal_imagen_report_pdf').report_action(self, data=data)


class ReportFiscal(models.AbstractModel):
    _name="report.ct_invoice_fiscal_imagen.ct_report_605"

    def _get_report_values(self, docids, data=None):
            model= self.env['ct.invoice.fiscal.imagen'].browse(int(data['form']['id']))
            return {
                'doc_ids': model.id,
                'doc_model': data['model'],
                'date_publish': time.strftime('%Y-%m-%d'),
                'company': self.env.user.company_id,
                'user': self.env.user,
                'docs': model,

            }




