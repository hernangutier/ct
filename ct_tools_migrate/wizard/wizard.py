import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _



class Migrate(models.TransientModel):
    _name="wz.migrate"
    product_id = fields.Many2one(
        'product.product',
        string='Seleccione el Producto para la linea de facturacion',
        ondelete='restrict',
        required=True,
        index=True)
    journal_id = fields.Many2one(
        'account.journal',
        string='Seleccione el Diario de Facturacion',
        ondelete='restrict',
        required=True,
        index=True)

    #---- Este Metodo Migra los Datos Pendiente ...
    def migrate(self):
        result=[]
        Tinvoice=self.env['ct.migrate.account.invoice'].search([('state','=','draft')])
        invoice=self.env['account.move'].search([])
        for inv in Tinvoice:
            # Creamos las Facturas correspondientes ---
            data_array=[]
            #---- Linea de Factura
            data=(0,0,{
                'product_id': self.product_id.id,
                'quantity': 1,
                'product_uom_id': 1,
                'price_unit': inv.amount_due
            })
            data_array.append(data)
            #--- Creamos la Factura
            new_invoice=invoice.create({
                'ref': inv.name,
                'partner_id': inv.partner_id.id,
                'journal_id': self.journal_id.id,
                'invoice_date': inv.date_invoice,
                'invoice_date_due': inv.date_due,
                'type': 'out_invoice',
                'invoice_line_ids': data_array
            })
            new_invoice.action_post()
            #--- Actualizamos el Registro
            result.append(inv.write({
                        'invoice_id': new_invoice.id,
                        'state': 'done'
                    }))

        return result

    def updateCost(self):
        products=self.env['ct.migrate.product.template'].search([])
        for p in products:
            tmpl=self.env['product.template'].search([
                ('old_sku','=',p.ref)
            ])
            if tmpl:
                tmpl.write({
                    'standar_price': p.cost
                })




