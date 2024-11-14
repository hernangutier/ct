import time
from datetime import date
import datetime
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Imagen de Factura Fiscal
#
#--------------------------------------------------------------------

class ImagenFiscal(models.Model):
    _name="ct.invoice.fiscal.imagen"
    name=fields.Char('#', default="/")
    number=fields.Char('Numero/Control Forma Libre')
    tax_bcv = fields.Float('Tasa de Cambio')
    igtf=fields.Float('IGTF 3%',compute="_calc_igtf")

    #------- Tipo para Clasificar el Documento
    type = fields.Selection([
        ('invoice', 'Factura'),
        ('note_credit', 'Nota de Credito'),
    ], string='Tipo/Doc', copy=False, index=True, default='invoice', store=True, required=True)

    #----- Calculamos el IGTF ------
    def _calc_igtf(self):
        for i in self:
            i.igtf=i.amount_total*0.03

    account_move_id = fields.Many2one(
        'account.move',
        string='Nota de Entrega de Origen',
        ondelete='restrict',
        index=True)

    account_tax_id=fields.Many2one(
        'account.tax',
        string='IVA',
        ondelete='restrict',
        index=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        index=True)


    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Termino de Pago',
        ondelete='restrict',
        index=True)

    state = fields.Selection([
        ('done', 'Activa'),
        ('cancel', 'Anulada'),
    ], string='Estado', copy=False, index=True, default='done', store=True, required=True)

    date_imagen=fields.Date('Fecha', default=datetime.date.today())
    date_due=fields.Date('Fecha de Vencimiento', compute='recalculate_due')
    amount_base=fields.Float('Base Imponible: ', compute='_compute_amount')
    amount_exento = fields.Float('Monto Exento: ', compute='_compute_amount')
    amount_tax=fields.Float('IVA', compute='_compute_amount')
    amount_total = fields.Float('Importe Total: ')
    line_ids = fields.One2many('ct.invoice.imagen.line', 'image_id', string='Lineas de Facturacion',
                                  copy=True,
                                  auto_join=True)

    def action_create_note_credit(self):
        pass

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })
        return self

    def action_post(self):
        self.write({
            'state': 'done'
        })
        return self

    def acion_print(self):
        #--- Imprimir Imagen de Factura
        pass


    @api.depends('line_ids')
    def _compute_amount(self):
        for i in self:
            base_i = 0
            exent = 0
            for l in i.line_ids:
                if l.product_id.is_exent:
                    exent+=l.price_sub_total
                else:
                    base_i+=l.price_sub_total
            i.amount_base=base_i
            i.amount_exento=exent
            i.amount_tax=i.amount_base*(((i.account_tax_id.amount/100)+1)) - i.amount_base
            i.amount_total=i.amount_base+i.amount_exento+i.amount_tax

    def recalculate_due(self):
      for i in self:
        i.date_due= i.date_imagen + datetime.timedelta(days=int((i.account_move_id.invoice_date_due - i.account_move_id.invoice_date).days))

    def action_make(self):
        for img in self:
            img.line_ids=[(5, 0, 0)]
            for note in img.account_move_id.line_ids:
                pass

    @api.model
    def create(self, vals):
        # self._check_lines_retrict(vals)
        if "name" not in vals or vals["name"] == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('nfiscal')
        image = super(ImagenFiscal, self).create(vals)
        return image



class ImagenLine(models.Model):
    _name="ct.invoice.imagen.line"
    _description="Lineas de Facturacion"

    image_id = fields.Many2one(
        'ct.invoice.fiscal.imagen',
        string='Linea Facturada',
        ondelete='restrict',
        index=True)

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        required=True,
        index=True)

    qty=fields.Integer('Cantidad')
    price=fields.Float('Precio')
    ref_unit = fields.Float('Ref. Unit')
    price_sub_total=fields.Float('Precio/SubTotal')


class AccountMove(models.Model):
    _inherit="account.move"

    def action_view_related_invoice_fiscal(self):
        domain = [('account_move_id', '=', self.id)]
        action = {
            'name': _('Imagenes Fiscales'),
            'type': 'ir.actions.act_window',
            'res_model': 'ct.invoice.fiscal.imagen',
            'view_type': 'tree,form',
            'view_mode': 'list,form',
            'context': {'edit': 1, 'create': 0, 'active_id': self.id},
            'domain': domain,
        }
        return action



#------------------------------------------------------
#
#
#    Clase que Modelo para Manejar las Tasas de Cambio
#
#
#------------------------------------------------------
class Tasa(models.Model):
    _name = "ct.invoice.imagen.tasa"

    value=fields.Float('Tasa BCV',digits=0, default=1.0)
    date=fields.Date('Fecha',require=True, index=True,
                       default=fields.Date.context_today)
    status=fields.Boolean('Activa (S/N)',default=True)

    _sql_constraints = [
        ('unique_name_per_day', 'unique (name)', 'Only one currency rate per day allowed!'),
        ('currency_rate_check', 'CHECK (rate>0)', 'The currency rate must be strictly positive.'),
    ]















