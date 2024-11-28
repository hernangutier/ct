import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


# --------------------------------------------------------------------
#
#   Listados de Clientes
#
# --------------------------------------------------------------------

class WzPartnerListPdf(models.TransientModel):
    _inherit = "ct.commons.wz.commons"
    _name = "ct.res.partner.list.pdf.wz"

    # --------- Estado de Preparacion de Pedido  --------
    type_class = fields.Selection([
        ('user', 'por Asesor/Ventas'),
        ('team', 'por Zona/Ventas'),
        ('state', 'por Estado'),
        ('pay', 'por Plazos de Pago'),

    ], string="Clasificacion/Agrupacion", default='user')

    # ----- Todos a Solo Uno  --------
    type_mod = fields.Boolean('General/Selectivo', default=True)

    # ---- Para Consultar por Asesor de Ventas
    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Zona de Ventas
    zone_id = fields.Many2one(
        'crm.team',
        string='Zona/Ventas',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Estado
    country_id = fields.Many2one(
        'res.country',
        string='Estado',
        ondelete='restrict',
        index=True)
    # ---- Para Consultar por Plazos de Pago
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Plazos de Pago',
        ondelete='restrict',
        index=True)

    def get_report(self):
        id = 0
        if self.type_class == 'user': id = self.user_id.id
        if self.type_class == 'team': id = self.zone_id.id
        if self.type_class == 'state': id = self.country_id.id
        if self.type_class == 'pay': id = self.payment_term_id.id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'group_type': str(self.type_class),
                'id': id,
            },
        }
        return self.env.ref('ct_res_partner.action_ct_res_partner_partner_list_pdf_wz_report').report_action(self, data=data)


class ReportWzPartnerListPdf(models.AbstractModel):
    _name = "report.ct_res_partner.ct_report_1000"

    def _get_report_values(self, docids, data=None):
        header_group = []
        title = 'Listado de Clientes segun Asesor '
        field_gruop = 'user_id'

        if data['form']['group_type'] == 'team':
            field_gruop = 'team_id'
            title = 'Listado de Clientes segun Zona de Ventas'

        if data['form']['group_type'] == 'state':
            field_gruop = 'state_id'
            title = 'Listado de Clientes segun el Estado'

        if data['form']['group_type'] == 'pay':
            field_gruop = 'pay_id'
            title = 'Listado de Clientes segun el Plazo de Pago'



        # ----- Consulta Agrupada  --
        grouped = self.env['res.partner'].read_group(
            [(field_gruop,'!=', None)],
            [field_gruop],
            [field_gruop]
        )
        #raise UserError(str(grouped))
        # ---- Creamos la Cabecera de Grupo oarreglo a trasnferir como parametro ----
        for g in grouped:
            if field_gruop == 'user_id':
                p = self.env['res.users'].browse(int(g.get(field_gruop)[0]))
                header_group.append({
                    'id': p.id,
                    'name': p.name
                })
            if field_gruop == 'team_id':
                p = self.env['crm.team'].browse(int(g.get(field_gruop)[0]))
                header_group.append({
                    'id': p.id,
                    'name': p.name
                })
            if field_gruop == 'state_id':
                    p = self.env['res.country.state'].browse(int(g.get(field_gruop)[0]))
                    header_group.append({
                        'id': p.id,
                        'name': p.name
                    })

        # ---- Consultamos los Registros en Bruto ---
        lines = self.env['res.partner'].search(
            [(field_gruop,'!=', None)],
            order=field_gruop)
        # ---- Retornamos los Parametros al Reporte -----

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'group_type': data['form']['group_type'],
            'company_id': self.env.user.company_id,
            'title': title,
            'user': self.env.user,
            'header': header_group,
            'lines': lines
        }
