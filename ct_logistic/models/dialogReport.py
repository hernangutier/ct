import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class dialogGuiaForComercial(models.TransientModel):
    _name="ct.logistic.dialog.guia.for.comercial"

    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container',
        ondelete='restrict',
        require=True,
        index=True)

    comercial_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        require=True,
        index=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'comercial_id': self.comercial_id.id,
                'container_id': self.container_id.id,
            },
        }
        return self.env.ref('ct_logistic.ct_logistic_report_805').report_action(self, data=data)


class dialogGuiaForComercialReport(models.AbstractModel):
    _name = "report.ct_logistic.ct_pdf_report_805"



    def _get_report_values(self, docids, data=None):
        #------ Recuperamos los Valores por el Dialogo ---
        comercial_id=int(data['form']['comercial_id'])
        container_id=int(data['form']['container_id'])
        #------ Realizamos la Consulta ------
        comercial=self.env['res.users'].browse(comercial_id)
        container=self.env['ct.logistic.container'].browse(container_id)
        orders=container.order_ids.filtered(lambda x: x.user_id.id==comercial_id).sorted(lambda y: y.partner_id.name, reverse=False)
        #----- Selecccionamos la Facturacion ---
        invoices=None
        for order in orders:
            inv=order.invoice_ids.filtered(lambda x: x.state=='posted')
            if len(inv)>0:
               if invoices:
                    invoices= invoices + inv
               else:
                   invoices=inv

        if invoices == None: raise UserError('No hay perdidos de el asesor: ' + comercial.partner_id.name)

        invoices=self.env['account.move'].browse(invoices.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'asesor': comercial.partner_id.name,
            'number': container.name,
            'descripcion': container.route,
            'chofer': container.chofer_id.name,
            'unidad': container.vehiculo_id.name,
            'company': self.env.user.company_id,
            'user': self.env.user,
            'docs': invoices,
        }

