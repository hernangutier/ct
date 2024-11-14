import time
from datetime import date
import datetime
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

# ----------------------------------------------------------
#
#    Dialogo para Crear la Imagen Fiscal
#
#
# ----------------------------------------------------------

class dialogImageFiscalForm(models.TransientModel):
    _name="ct.invoice.fisca.image.form"

    account_move_id = fields.Many2one(
        'account.move',
        string='Nota de Entrega de Origen',
        ondelete='restrict',
        index=True)

    account_tax_id = fields.Many2one(
        'account.tax',
        string='IVA',
        ondelete='restrict',
        required=True,
        index=True)

    number=fields.Char("# de Control F/L: ", required=True)

    tax_bcv=fields.Float('Tasa/Cambio BCV', required=True)

    @api.model
    def default_get(self,fields):
        res=super(dialogImageFiscalForm,self).default_get(fields)
        tax=self.env['ct.invoice.imagen.tasa'].search([],order="date desc",limit=1)
        if tax.value:
            if tax.date==datetime.date.today():
                res.update({
                    'tax_bcv': tax.value
                })
            else:
                raise UserError('Tasa de Cambio no esta Actualizada...')
        else:
            raise UserError('Tasa de Cambio no esta Actualizada...')
        return res


    def _check_invoice(self):
        inv=self.env['ct.invoice.fiscal.imagen'].search([
            ('account_move_id','=',self.account_move_id.id)
        ])
        if len(inv)>0:
            raise UserError('Ya existe una imagen fiscal asociada!')

    def action_post(self):
        self._check_invoice()
        lines_ids=[]
        for l in self.account_move_id.invoice_line_ids:

            vals = (0, 0, {
                'product_id': l.product_id.id,
                'qty': l.quantity,
                'ref_unit': l.price_unit,
                'price': (l.price_unit*self.tax_bcv),
                'price_sub_total': (l.price_unit*self.tax_bcv)*l.quantity,
            })
            lines_ids.append(vals)
        #--- Creamos la Factura
        image = self.env['ct.invoice.fiscal.imagen']
        image = image.create({
            'payment_term_id': self.account_move_id.invoice_payment_term_id.id,
            'number': self.number,
            'tax_bcv': self.tax_bcv,
            'account_move_id': self.account_move_id.id,
            'partner_id': self.account_move_id.partner_id.id,
            'account_tax_id': self.account_tax_id.id,
            'line_ids': lines_ids
        })
        return image


