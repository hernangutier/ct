import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Rutinas de Actualizacion Masiva
#
#--------------------------------------------------------------------

class UpdateTasaForm(models.TransientModel):
    _name="ct.update.tasa.form"

    percent=fields.Float('% a Aplicar', default=5.0)


    def post_update(self):
        products = self.env['product.template'].search([(
            'id', 'in', self.env.context.get('active_ids')
        )], order='name asc')
        for p in products:
            p.write({
                'percent': self.percent
            })
        return products


class ClientListReportForm(models.TransientModel):
    _name="ct.client.report.form"

    #--- Tipo de Reporte
    type = fields.Selection([
        ('gen', 'General'),
        ('usr', 'por Asesor'),
        ('team', 'por Zona de Ventas'),

    ], string='Tipo de Reporte', copy=False, index=True, default='gen', store=True, required=True)

    #---- Asesor de Ventas ----
    user_id = fields.Many2one(
        'res.users',
        string='Seleccione el Asesor de Ventas',
        ondelete='restrict',
        required=True,
        index=True)

    # ---- Canal de Ventas ----
    team_id = fields.Many2one(
        'crm.team',
        string='Seleccione la Zona de Ventas',
        ondelete='restrict',
        required=True,
        index=True)

    def get_report(self):
        pass
#----------------------------------------------------
#   Modelos para Reporte de Commisiones Generadas
#   En un Periodo
#
#----------------------------------------------------
class CommissionsForDateForm(models.TransientModel):
      _name="ct.sale.power.commissions.for.date.form"
      _inherit="ct.commons.wz.commons"
      for_users=fields.Boolean('Por Asesor', default=False)
      user_id = fields.Many2one(
          'res.users',
          string='Asesor/Ventas',
          ondelete='restrict',
          domain="[('sale_team_id','!=',None),('active','=',True)]",
          index=True)

      def get_report(self):
          self.validate()
          data = {
              'ids': self.ids,
              'model': self._name,
              'form': {
                  'date_init': str(self.date_init),
                  'date_end': str(self.date_end),

              },
          }
          return self.env.ref('ct_sale_power.action_ct_sale_power_report_1210').report_action(self, data=data)


class CommissionsForDateReportForm(models.AbstractModel):
    _name = "report.ct_sale_power.ct_pdf_report_1210"

    def _get_report_values(self, docids, data=None):
        docs=self.env['ct.sale.power.commissions'].search([
            ('state','=','account'),
            ('date_end','>=', data['form']['date_init']),
            ('date_end', '<=', data['form']['date_end']),
        ])
        return {

            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_init': data['form']['date_init'],
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'docs': docs,
        }

