import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzPartnerRaiting(models.TransientModel):
    _name="ct.sale.management.partner.raiting"
    _description="Raiting de Cliente"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido#',
        ondelete='restrict',
        require=True,
        index=True)

    partner_cliente_id=fields.Char('Cliente', related="sale_order_id.partner_id.name")

    partner_due=fields.Float('Saldo Actual: ', compute="_update_ui")





    #------ Facturas Abiertas
    account_move_ids = fields.Many2many('account.move', 'account_invoice_no_paid', string='Facturas', readonly=True)
    account_move_paid_ids = fields.Many2many('account.move', 'account_invoice_paid', string='Facturas', readonly=True)
    sale_order_stack_ids = fields.Many2many('sale.order', 'sale_order_stack_rel', string='Pedidos/Cola', readonly=True)
    payments_ids = fields.Many2many('account.payment', 'account_payment_stack_rel', string='Pagos/Registrados', readonly=True)




    #---- Cliente Activo -----
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        require=True,
        index=True)

    @api.depends('partner_id')
    def _update_ui(self):
        self.partner_due = self.partner_id.customer_due_amount
        self.account_move_ids = self.partner_id.invoice_ids.filtered(
            lambda x: x.state == 'posted' and x.type=='out_invoice' and x.invoice_payment_state!='paid')
        self.account_move_paid_ids = self.partner_id.invoice_ids.filtered(
            lambda x: x.state == 'posted' and x.type == 'out_invoice' and x.invoice_payment_state == 'paid')
        self.sale_order_stack_ids=self.partner_id.sale_order_ids.filtered(lambda x: x.invoice_status != 'invoiced' and x.state != 'cancel')
        self.payments_ids += self.env['account.payment'].search([('partner_id', '=', self.partner_id.id)])

