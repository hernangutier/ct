import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Modificacion al Picking para Preparacion de Pedidos
#
#--------------------------------------------------------------------
class StockPicking(models.Model):
    _inherit="stock.picking"

    state_preparations = fields.Selection([
        ('reserved', 'Reservado'),
        ('draft', 'en Cola'),
        ('packing', 'Embalado'),
        ('no', 'No Aplica'),
    ], string="Estado/Preparacion", default='draft')

    def action_cancel(self):
        obj=super(StockPicking, self).action_cancel()
        if self.state=='cancel':
            order=self.env['sale.order'].search([('name','=',self.origin)])
            self.write({
                'state_preparations': 'no'
            })
            for l in order:
                l.write({
                    'state': 'draft',
                    'state_preparations':'draft'
                })
        return  obj
    # ---- Marca o Fabricante --------
    asesor_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        index=True)

    state_id = fields.Many2one(
        'res.country.state',
        string='Estado',
        ondelete='restrict',
        index=True)

    city=fields.Char('Ciudad/Sector', default="N/A")


    @api.model
    def create(self, vals):
        #----- Actualizacion para Agrupar por Ubicacion y Asesores de Ventas los Picking ---
        if "asesor_id" not in vals or "state_id" not in vals or "city" not in vals:
            asesorId=self.env['res.partner'].browse(int(vals['partner_id']))
            if asesorId:
                vals.update(
                    {
                        'asesor_id': asesorId.user_id.id if asesorId.user_id  else None,
                        'city': asesorId.city if asesorId.city else 'N/A',
                        'state_id': asesorId.state_id.id if asesorId.state_id else None,
                     }
                )
        return super().create(vals)
