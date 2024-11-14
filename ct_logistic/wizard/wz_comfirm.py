import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzConfirm(models.TransientModel):
    _inherit="ct.sale.management.action.form.confirm"

    # ---- Marcadores de Despacho Inmediato ---
    close_immediate_dispatch = fields.Boolean('Cerrar Despacho a la Fecha', default=False)

    def action_inmediate_invoice(self):
        #--- Checamos que no este en un Container ---
        if self.close_immediate_dispatch:
            containers= self.env['ct.logistic.container'].search([('state','!=','done')])
            for c in containers:
                for o in c.order_ids:
                    if o.id==self.sale_order_id.id:
                       raise UserError('No se puede cerrar el pedido con la fecha de facturacion porque esta en un Container')

        self.sale_order_id.restrict_prepayment()
        self.PrevalidateOrder()
        self.check_limit_credit()

        # --- En este Verificamos las Dos Restricciones ---
        self.sale_order_id.check_rules_due('sale')
        self.sale_order_id.check_rules_due('invoice')
        
        self.sale_order_id.state_preparations = 'no'
        obj = self.sale_order_id.action_confirm()
        # ------- Validamos el Picking --------
        for pick in self.sale_order_id.picking_ids.filtered(lambda x: x.state == 'assigned'):
            imediate_obj = self.env['stock.immediate.transfer']
            pick.action_confirm()
            pick.action_assign()
            imediate_rec = imediate_obj.create({'pick_ids': [(4, pick.id)]})
            imediate_rec.process()
        # ------ Facturamos el Pedido ------
        self.action_invoice_commit()

        if self.close_immediate_dispatch:
            self.sale_order_id.close_dispatch_to_date()

        new_sale=self.env['sale.order'].browse(int(self.sale_order_id.id))
        return new_sale.action_view_invoice()

    def action_invoice_commit(self):
        self.sale_order_id._create_invoices()
        for inv in self.sale_order_id.invoice_ids:
            if inv.state == 'draft':
                if self.sale_order_id.recovery_expenses > 0:
                    # ---- Calculamos el Flete ----
                    line_fleet = []
                    fleet = inv.amount_total * (self.sale_order_id.recovery_expenses) / 100
                    line_fleet = ({
                        'product_id': 8,
                        'name': 'Gastos de Recuperacion de el ' + str(
                            self.sale_order_id.recovery_expenses) + ' % sobre' + str(inv.amount_total),
                        'quantity': 1,
                        'price_unit': fleet,
                        # 'credit': fleet,
                        'price_total': fleet
                    })

                    # ---- Actualzamos la Factura ----
                    inv.write({
                        'invoice_line_ids': [(0, 0, line_fleet)]
                    })

                inv.action_post()
        return self


class dialogInfologistic(models.TransientModel):
    _name="ct.dialog.info.logistic"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido#',
        ondelete='restrict',
        require=True,
        index=True)

    load=fields.Boolean('Cargado en Container', related="sale_order_id.load")
    info_delivered = fields.Text('Info/Container', related="sale_order_id.info_delivered")






