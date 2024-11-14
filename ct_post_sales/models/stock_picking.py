import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


#------------------------------------------------------------------
#
#     Modelo ProductTemplate Modificado para Control de Garantias
#
#------------------------------------------------------------------
class ProductTemplate(models.Model):
    _inherit = ["product.template"]
    #------ Clasificacion por Aplicacion del Producto --
    apply_type =  fields.Selection([
        ('eq', 'Equipo o Maquina'),
        ('rep', 'Repuesto o Pieza'),
        ('ins', 'Insumos'),
        ('dot', 'Dotacion'),
    ], string='Tipo por Aplicacion o Uso', copy=False, index=True, default='rep', store=True, required=True)

    # ---- Clasificador -------------
    tabulator_clas_id = fields.Many2one(
        'ct.post.sales.tabulator.clas',
        string='Clasificador Tabulador',
        ondelete='restrict',
        index=True)

    #---- Relacion para Link de Repuestos a Equipos ----
    equip_compatibility_ids = fields.Many2many(
        'product.product', string='Equipos Compatibles', domain="[('apply_type','=','eq')]")

    def action_view_spare_part(self):
        self.ensure_one()
        domain=[('equip_compatibility_ids','in',self.id)]
        action = {
            'name': _('Repuestos Compatibles'),
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref("ct_post_sales.view_ct_post_sales_product_template_kanban").id,
            'res_model': 'product.template',
            'view_mode': 'kanban',
            'domain': domain
        }
        return action

    #------- Muestra las Ultimas Facturas de el Equipo
    def action_view_last_invoices(self):
        self.ensure_one()
        domain = [('product_id', '=', self.product_variant_id.id)]
        action = {
            'name': _('Ultima Facturacion del Equipos'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'domain': domain
        }
        return action
    #---- Relacion para Enlazar con Catalogo de Partes


#------------------------------------------------------------------------
#
#     Modelo stock.pricking Modificado para Transferencias y Descargas
#
#-------------------------------------------------------------------------

class StockPicking(models.Model):
    _inherit="stock.picking"

    os_id = fields.Many2one('ct.p.s.order.service', string='Solicitudes Repuestos',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
                              help="Solicitud...")

    #----- Metodo para checar la Disponibilidad de las Exsistencias a Solicitar ---
    def check_disponibility(self):
        for l in self.move_ids_without_package:
            if l.product_uom_qty > l.product_id.qty_available:
                raise UserError('El Producto :' + l.product_id.name + ' ' + 'no tiene disponbilidad')

    #----- Metodo para Activar Opciones disponibles solo para esta Interfaz Grafica ---
    def action_post(self):
        self.ensure_one()
        self.action_reserved()
        self.action_confirm()
        ###self.button_validate()
        imediate_obj = self.env['stock.immediate.transfer']
        imediate_rec = imediate_obj.create({'pick_ids': [(4, self.id)]})
        imediate_rec.process()
        obj = self.write({
            'state_preparations': "packing"
        })
        return obj

    def action_reserved(self):
        #----- Checamos si esta preparado para hacer la reserva
        self.ensure_one()
        self.check_disponibility()
        self.action_assign()

    def action_free_reserved(self):
        self.ensure_one()
        self.do_unreserve()


class StockMove(models.Model):
    _inherit="stock.move"

    quantity_available=fields.Float('Qty. Disp', compute="_get_qty_disp")

    @api.depends('product_id','product_uom_qty')
    def _get_qty_disp(self):
        for l in self:
            qty=self.env['stock.quant'].search([
                ('product_id','=',l.product_id.id),
                ('location_id','=',l.picking_id.location_id.id)
            ], limit=1)
            l.update({
                'quantity_available': qty.quantity-qty.reserved_quantity
                     })

    @api.onchange('product_id','picking_type_id')
    def onchange_product(self):
        super(StockMove, self).onchange_product()
        #---- Verificamos que el Repuesto aplique al Equipo en Question ---
        if self.picking_id.os_id:
            #---- es una order de Servicio
          if self.product_id:

            if len(self.product_id.equip_compatibility_ids.filtered(lambda x: x.id==self.picking_id.os_id.product_id.id))==0:
               raise UserError('Este Producto no aplicac compatibilidad al equipo: ' + self.picking_id.os_id.product_id.name)











