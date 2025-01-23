import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#   Sale.Order Adaptado para Funcionamiento Mayorista y Pedidos Moviles
#
#--------------------------------------------------------------------

class SaleOrder(models.Model):
    _inherit="sale.order"


    # --------------------------------------------------------------------
    #
    #   Funciones de Computo sobre Sale.Order
    #
    # --------------------------------------------------------------------
    #----- Conteo de las Lineas ----
    def _compute_order_line_count(self):
        # ------------ Contador de Lineas de Pedido ----
        self.order_line_count = len(self.order_line)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.team_id:
            self.team_id = self.partner_id.team_id
            self.city=self.partner_id.city if self.partner_id.city else None
            self.state_id = self.partner_id.state_id.id if self.partner_id.state_id else None

        if self.partner_id.property_product_pricelist:
            self.pricelist_id = self.partner_id.property_product_pricelist

        if self.partner_id.property_payment_term_id:
            self.payment_term_id = self.partner_id.property_payment_term_id

    # ------ Enviar a Almacen solo pedidos Reservados ----
    def action_send_to_storage(self):
        if self.departament_id.confirm_invoice_inmediate:
            return {
                'name': _('Procesar/Pedido'),
                'context': {'active_id': self.id},
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ct.sale.management.action.form.confirm',
                'view_id': self.env.ref("ct_sale_management.view_ct_sale_management_wz_confirm").id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            if self.state_preparations == 'reserved' or self.state_preparations == 'draft':
                if self.state=='sale':
                    self.state_preparations = "storage"
                    for l in self.picking_ids.filtered(lambda x: x.state=='assigned'):
                        l.write({
                            'state_preparations': 'draft'
                        })

                else:
                    raise UserError('El pedido no esta reservado para ser enviado a Embalaje...')
            else:
                    raise UserError('El pedido no esta reservado para ser enviado a Embalaje...')

    #--- Action Aumentar Credito para Pedido ---
    def action_load_limit_credit(self):
        pass

    #------ Facturar despues de Embalado ---
    def action_create_invoice(self):
      if self.state=='cancel':
          raise UserError("Pedido se encuentra cancelado...")
      else:
        self._create_invoices()
        for i in self.invoice_ids:
            i.action_post()

    def _get_consolidated(self):
        for s in self:
            count = 0
            for l in s.order_line:
                l_filter = l.filtered(lambda x: x.product_id.departament_id.confirm_invoice_inmediate == True)
                for f in l_filter:
                    count += f.qty_delivered
            s.consolidated_count = count

    #----------------------------------------------------------------------
    #------------------------  Campos Nuevos Agregados     ----------------
    #----------------------------------------------------------------------
    # --------- Estado de Preparacion de Pedido  --------
    state_preparations = fields.Selection([
            ('draft', 'en Espera'),
            ('reserved', 'Reservado'),
            ('storage', 'en Almacen'),
            ('packing', 'Embalado'),
            ('no', 'No Aplica'),
    ], string="Estado/Preparacion", default= 'draft')

    not_control_dep=fields.Boolean('Sin/Control Departamental', default=True)

    packing_register = fields.Integer('Paquetes/Bultos', default=0)

    consolidated_count=fields.Integer('Carga/Consolidada', compute="_get_consolidated")

    # ------ Departamento de Facturacion Asignado
    departament_id = fields.Many2one(
        'ct.product.departament',
        string='Departamento/Facturacion',
        ondelete='restrict',
        required=True,
        index=True)

    #--- Contador de Lineas de Pedido -----
    order_line_count = fields.Integer('Total Lineas: ', compute="_compute_order_line_count")
    #-------- Campos para Consultas Ubicaciones de los Pedidos ----
    state_id = fields.Many2one(
        'res.country.state',
        string='Estado/Provincia',
        ondelete='restrict',
        index=True)
    city = fields.Char('Ciudad/Sector', default="N/A")
    #--------------------------------------------------------------

    #---- Campo Nuevo para ver Notas sobre el Pedido ---

    # ----------------------------------------------------------------------
    # ------------------------   Actualizar Precios         ----------------
    # ----------------------------------------------------------------------

    @api.onchange('pricelist_id', 'partner_id')
    def _onchange_price_recalculation(self):
        """this method use to show the product price according to the sales order price list"""
        if self.partner_id and self.pricelist_id:
            for line in self.order_line:
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id,
                    fiscal_position=line.env.context.get('fiscal_position')
                )
                line.price_unit = self.env['account.tax']._fix_tax_included_price_company(
                    line._get_display_price(product), product.taxes_id, line.tax_id, line.company_id)

    @api.onchange('pricelist_id', 'partner_id')
    def _onchange_discount_recalculation(self):
        """this method is mainly used for the discount price calculate according to the price list"""
        if self.partner_id and self.pricelist_id:
            for line in self.order_line:
                if not (line.product_id and line.product_uom and
                        line.order_id.partner_id and line.order_id.pricelist_id and
                        line.order_id.pricelist_id.discount_policy == 'without_discount' and
                        self.env.user.has_group('product.group_discount_per_so_line')):
                    return

    @api.onchange('order_line')
    def _onchange_order_line(self):
        #----- Controlamos un Maximo de 20 Lineas de Pedido por Pedido
        if len(self.order_line)>20:
            raise UserError('Limite de Lineas de Pedido alcanzado!')
        #--------------------------------------------------------------
        self.order_line_count = len(self.order_line)
        if not self.departament_id:
            raise UserError('Debe seleccionar un departamento de Facturacion o Ventas!')
        for l in self.order_line:
            value = self.order_line.filtered(lambda f: f.product_id == l.product_id)
            if not self.departament_id.restrict_control_homogen:
                items_dep = len(
                    self.order_line.filtered(lambda f: f.product_id.departament_id.id != self.departament_id.id))
                if items_dep > 0:
                    raise UserError('Existen Productos de otros Departamentos de Ventas! ')
            if len(value) > 1:
                raise UserError('El Producto: ' + l.product_id.display_name + ' ya esta cargado en la orden!')

    # ----------------------------------------------------------------------
    # ------------------------   Override Confirm          -----------------
    # ----------------------------------------------------------------------
    def action_confirm(self):
        for order in self:
            line=order.order_line
            for l in line:
                if  l.product_uom_qty>l.product_id.qty_available:
                    notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': ('Error de Restriccion'),
                            'message': 'Producto: ' + l.product_id.display_name + ' con existencia agotada!' ,
                            'type': 'danger',  # types: success,warning,danger,info
                            'sticky': False,  # True/False will display for few seconds if false
                        },
                    }
                    return notification


        res = super(SaleOrder, self).action_confirm()
        return res

    def action_cancel(self):
        if self.state_preparations=='storage':
            raise ValidationError('Pedido no se puede cancelar esta en control de almacen')
        if self.invoice_status=="invoiced":
            raise ValidationError('Pedido se encuentra Totalmente Factutarado debe Realizar una Devolucion...')

        res = super(SaleOrder, self).action_cancel()
        return res

    def anular(self):
        #-- Verificamos que Tenga Movimiento de de Devolucion Completo --
        for l in self.order_line:
            if l.qty_delivered>0:
                raise UserError('El Pedido no esta totalmente devuelto')
        for inv in self.invoice_ids:
            inv.button_draft()
            invt.button_cancel()


    def set_invoiced(self):
        if len(self.invoice_ids.filtered(lambda x: x.state=='posted'))==0:
            raise UserError('No se puede cerrar como facturado porque esta pendiente por Facturar...')
        else:
            self.invoice_status='invoiced'


    def justified_qty_units(self):
        if self.state not in  ('draft','sent'):
            raise UserError('No se pueden auto-ajustar unidades pedidas porque el pedido no es un Presupuesto...')
        for lines in self.order_line:
            if lines.product_uom_qty>lines.product_id.qty_available:
                if lines.product_id.qty_available>0:
                    lines.write({
                        'product_uom_qty': lines.product_id.qty_available
                    })
                else:
                    lines.unlink()

    @api.model
    def create(self, vals):
        if "payment_term_id" not in vals or vals["payment_term_id"] == False:
           raise UserError('Debe establecer un Plazo de Pago')
        return super().create(vals)

    def write(self,vals):
        if "payment_term_id" not in vals:
            if not self.payment_term_id:
                raise UserError('Debe establecer un Plazo de Pago')
        else:
            if vals["payment_term_id"] == False:
                raise UserError('Debe establecer un Plazo de Pago')

        return super().write(vals)