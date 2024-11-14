import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class ProductMigrate(models.Model):
    _name="ct.migrate.data.product.template"
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
    departament_id = fields.Many2one(
        'ct.product.departament',
        string='Departamento',
        ondelete='restrict',
        require=False,
        index=True)
    categ_id = fields.Many2one(
        'product.category',
        string='Categoria',
        ondelete='restrict',
        require=False,
        index=True)


    ubicado=fields.Boolean('Ubicado (s/n)', default=False)




    def updateCost(self):
        products = self.env['ct.migrate.data.product.template'].search([])
        for p in products:
            tmpl = self.env['product.product'].search([
                ('old_sku', '=', p.ref)
            ], limit=1)
            if tmpl:
                tmpl.write({
                    'standard_price': p.cost,

                })

    def setAsesorPicking(self):
        #pick=self.env['stock.picking'].search([])
        #for p in pick:
        #    p.write({
        #        'asesor_id': p.partner_id.user_id.id if p.partner_id.user_id else None
        #    })
        #sale=self.env['sale.order'].browse(364)
        #sale.write({
        #    'state': 'sale'
        #})
        sales= self.env['sale.order'].search([])
        for s in sales:
          if s.payment_term_id:
            s.write({
                'team_id': s.partner_id.team_id.id if s.partner_id.team_id else None,
                'city': s.partner_id.city if s.partner_id.city else None,
                'state_id': s.partner_id.state_id.id if s.partner_id.state_id else None,
            })

    def generateSku(self):
        products= self.env['product.template'].search([], order="name asc")
        for p in products:
            p.write({
                'default_code': self.env['ir.sequence'].next_by_code('product.product')
            })

    def createProducts(self):
        tmpl=self.env['product.template']
        products = self.env['ct.migrate.data.product.template'].search([(
            'ubicado','=',False
        )])
        for p in products:
            tmpl.create({
                'name': p.name,
                'categ_id': p.categ_id.id,
                'departament_id': p.departament_id.id,
                'standard_price': p.cost,
                'old_sku': p.ref,
                'location_fisical_id': 1
            })



    def identificar(self):
        products = self.env['ct.migrate.data.product.template'].search([])
        for p in products:
            tmpl = self.env['product.product'].search([
                ('old_sku', '=', p.ref)
            ], limit=1)
            if tmpl:
                p.ubicado=True
                p.product_id=tmpl.id






    def updateQty(self):
            data=[]
            products = self.env['ct.migrate.data.product.template'].search([
                ('ubicado','=',True)
            ])
            for p in products:
                   vals = (0, 0, {
                        'product_id': p.product_id.id,
                        'product_qty': p.inv,
                        'location_id': 14
                    })
                   data.append(vals)

            #--- Consultamos el Inventario
            inv=self.env['stock.inventory'].browse(2)
            inv.write({
                'line_ids': data
            })



