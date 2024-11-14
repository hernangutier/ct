import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Modelo para Implementar Nuevo Reporte Factura-Nota de Entrega
#
#--------------------------------------------------------------------



class ReportAccountMove(models.AbstractModel):
    _name="report.ct_sale_management.action_account_move_report_pdf"

    def _get_report_values(self,docids,data=None):
        report_obj=self.env['ir.action.report']
        report=report_obj._get_report_from_name('ct_sale_management.action_account_move_report_pdf')
        return {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'docs': self.env['account.move'].browse(docids),
            'company': 'Hola',
        }



class AccountMove(models.Model):
    _inherit="account.move"

    # --- Campos Nuevos para Inforamcion Logistica a la Fcatura
    packing_register = fields.Integer('Bultos', default=0, compute="_get_info")

    # ------ Departamento de Facturacion Asignado
    departament_id = fields.Many2one(
        'ct.product.departament',
        string='Departamento/Facturacion',
        ondelete='restrict',
        compute='_get_info',
        required=True,
        index=True)

    def _get_info(self):
        for l in self:
            if l.invoice_origin:
               #---- Recuperamos el Pedido ---
               saleOrder=self.env['sale.order'].search([
                   ('name','=',l.invoice_origin)
               ])
               if len(saleOrder)>=1:
                   #----- Pedido Ubicado ---
                   l.packing_register=saleOrder.packing_register
                   if saleOrder.departament_id :
                       l.departament_id = saleOrder.departament_id.id
                   else:
                       l.departament_id=None
               else:
                   l.packing_register=0
            else:
                    l.packing_register=0

