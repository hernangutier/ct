import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzPrwoductReserved(models.TransientModel):
    _name="ct.sale.management.product.reserved"

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto: ',
        ondelete='restrict',
        require=True,
        index=True)



    stock_move_ids = fields.Many2many('stock.move', 'stock_move_product_reserved_rel', string='Reservas',
                                   compute='_update_ui',   readonly=True)

    @api.depends('product_tmpl_id')
    def _update_ui(self):
        #---- Consultamos el id de product.produtc
        product_id=self.env['product.product'].search([('product_tmpl_id','=',int(self.product_tmpl_id.id))], limit=1)
        #raise UserError(product_id.id)
        #---- Actualizamos los Movimientos ----
        self.stock_move_ids+= self.env['stock.move'].search([
                                ('product_id','=',int(product_id.id))
                                ]).filtered(lambda x: x.picking_id.state=='assigned' and x.picking_type_id.code=='outgoing')
