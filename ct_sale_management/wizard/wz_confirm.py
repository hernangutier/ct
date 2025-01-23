import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class WzConfirm(models.TransientModel):
    _name="ct.sale.management.action.form.confirm"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido#',
        ondelete='restrict',
        require=True,
        index=True)

    partner_name=fields.Char('Cliente', readonly=True, related='sale_order_id.partner_id.name')
    partner_state_name = fields.Char('Estado/Provincia', readonly=True, related='sale_order_id.partner_id.state_id.name')

    partner_state_location_name = fields.Char('Ciudad/Pueblo/Caserio', readonly=True, related='sale_order_id.partner_id.locations_id.name')
    user_name = fields.Char('Asesor/Ventas', readonly=True, related='sale_order_id.user_id.name')
    departament_sale=fields.Char('Departamento/Ventas', readonly=True, related='sale_order_id.departament_id.name')
    inmediate_invoice=fields.Boolean('Factura de Inmediato', readonly=True, related="sale_order_id.departament_id.confirm_invoice_inmediate")



    # ------ Totales ---------
    currency_id = fields.Many2one("res.currency", related='sale_order_id.pricelist_id.currency_id', string="Currency", readonly=True,
                                  required=True)
    amount_total=fields.Monetary(string='Total', readonly=True, related="sale_order_id.amount_total" )
    amount_untaxed = fields.Monetary(string='Base Imponible', readonly=True, related="sale_order_id.amount_untaxed")
    order_line_count = fields.Integer('Total Lineas: ', related="sale_order_id.order_line_count", readonly=True)


    def update_state_picking(self,state):
        for pick in self.sale_order_id.picking_ids.filtered(lambda x: x.state=='assigned'):
            pick.write({
                'state_preparations': state
            })

    #----- Reservar Pedido ---
    def action_reserved(self):
        #------ Validamos la Orden
        if not len(self.sale_order_id.payment_term_id.line_ids.filtered(lambda x: x.days == 0)) > 0:
            # ---- Verificamos si no es Prepagado para que Omita la Regla de Limite de Credito
            self.PrevalidateOrder()
            self.check_limit_credit()
            self.sale_order_id.check_rules_due('sale')
        #------------------------
        obj=self.sale_order_id.action_confirm()
        if self.sale_order_id.state=='sale':
            obj=self.sale_order_id.write({
                'state_preparations': 'reserved'
            })
            #---- Actualizamos el Picking ---
            self.update_state_picking('reserved')

        return obj

    #----- Enviar a Almacen para Preparar
    def action_preparate(self):
        self.PrevalidateOrder()
        self.check_limit_credit()
        self.sale_order_id.check_rules_due('sale')
        if self.sale_order_id.state=="sale":
            self.sale_order_id.state_preparations = 'storage'
            self.update_state_picking('draft')
        else:
            obj = self.sale_order_id.action_confirm()
            if self.sale_order_id.state=='sale':
                self.sale_order_id.state_preparations = 'storage'
                self.update_state_picking('draft')

        return obj

    def check_limit_credit(self):
        if self.sale_order_id.partner_id.control_credit:
            if self.sale_order_id.partner_id.credit_limit == 0:
                raise UserError("Limite de Credito no establecido!")
                #return self.do_notify("Restriccion", "Limite de Credito no establecido!", 'danger')
            if self.sale_order_id.partner_id.credit_disponible < 0:
                raise UserError("Credito disponible Agotado!")
            elif self.sale_order_id.partner_id.credit_disponible < self.sale_order_id.amount_total:
                raise UserError("Credito disponible insuficiente!")


    def PrevalidateOrder(self):

        #------ Validaciones de Contacto ------
        if not self.sale_order_id.payment_term_id:
            raise UserError('Debe Establecer un Plazo de Pago...')
        if not self.sale_order_id.partner_id.city:
            raise UserError('Debe Establecer la Ciudad o Sector donde se ubica Cliente...')
        if not self.sale_order_id.partner_id.state_id:
            raise UserError('Debe Establecer el Estado donde se ubica Cliente...')
        #--------------------------------------
        for lines in self.sale_order_id.order_line:
            if lines.price_unit==0:
                raise UserError('El Producto: ' + lines.product_id.display_name + ' no tiene precio establecido!')
            if lines.price_unit< float('{0:.2f}'.format(lines.product_id.standard_price)):
                raise UserError('El Producto: ' + lines.product_id.display_name + ' tiene Precio por debajo de el Costo!')
        #---- Caso I si es un Presupuesto
        if self.sale_order_id.state in ('draft','sent'):
            for l in self.sale_order_id.order_line:
                if l.product_uom_qty>(l.product_id.qty_available-l.product_id.outgoing_qty):
                    raise ValidationError('Producto: '+ l.product_id.name + " tiene existencia agotada tomando en cuenta las reservas...")
        #---- Caso II pedido confirmado
        if self.sale_order_id.state=='sale':
            if self.sale_order_id.state_preparations=='storage':
                raise ValidationError('Pedido en Control de Almacen... no puede ser facturado hasta que no se procese...')

    #---- Verifica si es Prepago y Tiene Disponibilidad de Pago

    #----- Prepara Valida y Factura de inmediato ----
    def action_inmediate_invoice(self):
        #---- Prevalidamos la Order
        #---- Checking Not Invoice Order si es Prepago ---

        self.PrevalidateOrder()
        self.restrict_prepayment()
        self.check_limit_credit()

        #--- En este Verificamos las Dos Restricciones ---
        self.sale_order_id.check_rules_due('sale')
        self.sale_order_id.check_rules_due('invoice')
        #------------------------------------------------
        self.sale_order_id.state_preparations = 'no'
        obj = self.sale_order_id.action_confirm()
        #------- Validamos el Picking --------
        for pick in self.sale_order_id.picking_ids.filtered(lambda x: x.state=='assigned'):
            imediate_obj = self.env['stock.immediate.transfer']
            pick.action_confirm()
            pick.action_assign()
            imediate_rec = imediate_obj.create({'pick_ids': [(4, pick.id)]})
            imediate_rec.process()
        #------ Facturamos el Pedido ------

        self.sale_order_id._create_invoices()
        for inv in self.sale_order_id.invoice_ids:
            if inv.state=='draft':
                inv.action_post()
        #--- Descargar Automaticamente el PDF
        #---- Retornamos la Vista de Facturacion --
        raise UserError('Si Pasa')
        #return obj
