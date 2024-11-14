import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class Summary(models.TransientModel):
    _name="ct.logistic.container.summary"
    _description="Resumen de la Guia"

    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container',
        ondelete='restrict',
        require=True,
        index=True)


    sale_order_count= fields.Integer('#Pedidos/Cargados', compute="_get_calc_summary")
    amount_packing=fields.Integer('#Paquetes: ', compute="_get_calc_summary")
    amount_invoiced=fields.Float("Total Facturado", compute="_get_calc_summary")
    paradas_count=fields.Integer('Paradas/Despacho', compute="_get_calc_summary")

    @api.depends('container_id')
    def _get_calc_summary(self):
        self.sale_order_count = len(self.container_id.order_ids)
        for order in self.container_id.order_ids:
            self.amount_packing += order.packing_register
            for inv in order.invoice_ids.filtered(lambda x: x.state == 'posted' and x.type == 'out_invoice'):
                self.amount_invoiced += inv.amount_total
        orders=self.env['sale.order'].search([])
        grouped=orders.read_group(
            [('id', 'in', self.container_id.order_ids.ids)],
            ['partner_id:avg'],
            ['partner_id']
        )
        self.paradas_count=len(grouped)