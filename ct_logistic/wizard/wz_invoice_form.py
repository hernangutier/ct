import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzInvoiceForm(models.TransientModel):
    _name="ct.logistic.wz.invoice.form"
    _description="Dialogo de Facturacion"



    # --------- Ruta Sugerida --------
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido',
        ondelete='restrict',
        require=True,
        index=True)

    items_to_invoice=fields.Integer('Items a Facturar: ', compute='_items_to_invoice')

    delivered_expenses=fields.Float('% Gastaos Recuperacion', related='sale_order_id.recovery_expenses')
    delivery_expenses_amount=fields.Float('Total Gastos/Recuperacion: ')
    invoice_amount=fields.Float('Total a Facturar $', compute='_items_to_invoice')

    @api.depends('sale_order_id')
    def _items_to_invoice(self):
        count=0
        amount=0
        for items in self.sale_order_id.order_line:
            if items.qty_delivered-items.qty_invoiced!=0:
                amount+=items.price_subtotal
                count+=1
        self.items_to_invoice=count
        self.invoice_amount=amount
        self.delivery_expenses_amount=self.invoice_amount*(self.delivered_expenses/100)

    def action_invoice_commit(self):
        self.sale_order_id.restrict_prepayment()
        self.sale_order_id.check_rules_due('invoice')
        if self.sale_order_id.invoice_status=='invoiced':
            raise UserError('El pedido ya esta Facturado!')
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