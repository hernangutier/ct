import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class WzPickingPost(models.TransientModel):
    _name="ct.sale.management.picking.action.form.post"

    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking#',
        ondelete='restrict',
        require=True,
        index=True)


    packing_register=fields.Integer('Paquetes/Bultos', default=1)

    type=fields.Integer(default=1)

    def action_post(self):
         #------ Obtenemos las Ordenes ---

         #------ Checamos la Lineas si estan Correctas
         if self.type==1:
            if self.picking_id.state!='assigned':
                raise UserError('No hay disponibilidad!')
            if  self.picking_id.state_preparations =='reserved':
                raise UserError('Pedido esta en Reserva necesita aprobacion de Ventas')
            #---- Validamos el Picking
            imediate_obj = self.env['stock.immediate.transfer']
            imediate_rec = imediate_obj.create({'pick_ids': [(4, self.picking_id.id)]})
            imediate_rec.process()
            obj=self.picking_id.write({
                'state_preparations' : "packing"
            })
            #---- Facturamos el Pedido ---
            sale = self.env['sale.order'].search([('name', '=', self.picking_id.origin)], limit=1)
            sale._create_invoices()
            for inv in sale.invoice_ids:
                if inv.state == 'draft':
                    inv.action_post()
            #---- Actualizamos el Pedido
            if sale:
                sale.write({
                    'state_preparations': 'packing',
                    'packing_register': self.packing_register
                })
            return obj
         else:
             if sale:
                 sale.write({
                     'state_preparations': 'packing',
                     'packing_register': self.packing_register
                 })
             return self

