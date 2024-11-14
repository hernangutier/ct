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


    def updateMaster(self):
        products = self.env['ct.migrate.data.product.template'].search([])
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
            products = self.env['ct.migrate.data.product.template'].search([])
            for p in products:
                tmpl = self.env['product.product'].search([
                    ('old_sku', '=', p.ref)
                ])
                if tmpl:
                    p.write({
                        'product_id': tmpl.id
                    })