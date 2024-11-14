import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#---------------------------------------------------------
#
#   Este Modelo Almacena los datos importados desde Excel
#   de Migracion para Posteriormente Crear las Facturas
#   Necesarias ....
#----------------------------------------------------------
class AccountMove(models.Model):
    _name='ct.migrate.account.invoice'
    #--- Numero de Fcatura anterior
    name=fields.Char()
    #Fecha -----
    date_invoice=fields.Date('Fecha/Doc')
    date_due=fields.Date('Fecha/Vence')
    # Cliete ----
    ref_invoice=fields.Char('Factura/Referenciada')

    partner_id=fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        required=True,
        index=True)

    invoice_id = fields.Many2one(
        'account.move',
        string='Ref. Factura',
        ondelete='restrict',
        required=False,
        index=True)

    #---- Monto Actual Deuda
    amount_due=fields.Float('Saldo/Deudor')
    #--- Estatus del Registro ---
    state = fields.Selection([
        ('draft', 'en Espera'),
        ('done', 'Procesado'),

    ], string='Estatus', copy=False, index=True, default='draft', store=True, required=True)


class ProductMigrate(models.Model):
    _name="ct.migrate.product.template"
    ref=fields.Char('Referencia', required=True)
    name=fields.Char('Descripcion', required=True)
    cost=fields.Float('Costo')
    inv= fields.Integer('qty',default=0)
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        require=False,
        index=True)


    def updateMaster(self):
        products = self.env['ct.migrate.product.template'].search([])
        for p in products:
            tmpl = self.env['product.template'].search([
                ('old_sku', '=', p.ref)
            ])
            if tmpl:
                tmpl.write({
                    'standard_price': p.cost
                })

    def updateQty(self):
            data=[]
            products = self.env['ct.migrate.product.template'].search([])
            for p in products:
                tmpl = self.env['product.product'].search([
                    ('old_sku', '=', p.ref)
                ])
                if tmpl:
                    p.write({
                        'product_id': tmpl.id
                    })











