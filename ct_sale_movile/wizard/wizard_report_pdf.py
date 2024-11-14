import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#-------------------------------------------------------------
#   Reportes Pdf Pedidos Moviles para Auditar
#ct.commons.wz.commons
#-------------------------------------------------------------
class WzSaleOrderMovileList(models.TransientModel):
    _inherit = "ct.commons.wz.commons"
    _name = "ct.sale.order.movile.wz.sale.order.movile.list"

    def get_report(self):
        self.title = "Pedidos Moviles Listado"
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'title': self.title,
                'date_init': self.date_init,
                'date_end': self.date_end
            },
        }
        return self.env.ref('ct_sale_movile.report_sale_order_movile').report_action(self, data=data)


class ReportSaleOrderMovileList(models.AbstractModel):
    _name="report.ct_sale_movile.sale_order_movile_list_report_view"

    def _get_report_values(self,docids,data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'company': self.env.user.company_id,
            'lines': self.env['ct.sale.order.movile'].search_read([], order='create_date'),
            'title': data['form']['title']
        }