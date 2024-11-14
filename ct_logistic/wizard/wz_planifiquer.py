import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class Planifiquer(models.TransientModel):
    _name="ct.logistic.planifiquer"
    _description="Planificador de Rutas de Despacho"

    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container',
        ondelete='restrict',
        require=True,
        index=True)

    user_id = fields.Many2one(
        'res.users',
        string='Asesor/ventas',
        ondelete='restrict',
        require=True,
        index=True)

    count_sale_order=fields.Integer('#Pedidos Pendientes a Cargar: ', compute="_get_count_sale_order_wait")

    @api.depends('user_id')
    def _get_count_sale_order_wait(self):
        s=self.env['sale.order'].search([
            ('state','=', 'sale'),
            ('invoice_status', '=','invoiced'),
            ('state_delivered','=',False),
            ('is_load','=',False),
            ('user_id','=',self.user_id.id)
        ])
        filter=s.filtered(lambda x: x.is_load==False)
        self.count_sale_order= len(filter)


    def action_post(self):
        lines = []
        sale_orders=self.env['sale.order'].search([
            ('state','=', 'sale'),
            ('invoice_status', '=','invoiced'),
            ('state_delivered','=',False),
            ('user_id','=',self.user_id.id)
        ])

        filter=sale_orders.filtered(lambda x: x.is_load==False)

        if len(filter)!=0:
            #--- Agrupamos las Ordenes
            for s in filter:
                vals = (0, 0, {
                    'sale_order_id': s.id,
                    'state': 'draft'
                })
                lines.append(vals)
            self.container_id.write({
                'container_line_ids' : lines
            })
        else:
            raise UserError('No Hay Pedidos Disponibles...')












