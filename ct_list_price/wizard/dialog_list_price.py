import time
import datetime
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

# ----------------------------------------------------------
#
#    Modelo Para Gestionar Dialog de Lista de Precios
#
#
# ----------------------------------------------------------

class dialogListPrice(models.TransientModel):
    _name="ct.list.price.dialog.list.price"

    type = fields.Selection([
        ('brand', 'por Marca'),
        ('categ', 'por Categoria'),
    ], string='Tipo/Reporte', copy=False, index=True, default='categ', store=True)





    categ_id = fields.Many2one(
        'product.category',
        string='Categoria de Producto',
        ondelete='restrict',
        index=True)

    brand_id = fields.Many2one(
        'ct.product.brands',
        string='Marca o Fabricante de el Producto',
        ondelete='restrict',
        index=True)

    list_price_id = fields.Many2one(
        'product.pricelist',
        string='Tarifa',
        ondelete='restrict',
        required=True,
        index=True)

    with_exist=fields.Boolean('Con Existencias (S/N)', default=False)

    title=fields.Char()

    def get_report(self):
        if self.type=='categ':
            self.title=self.categ_id.name
        else:
            self.title=self.brand_id.name

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'value_search': int(self.categ_id.id) if self.type=='categ' else int(self.brand_id.id),
                'bool_exist': self.with_exist,
                'list_price_id': self.list_price_id.id,
                'type': str(self.type)
            },
        }
        return self.env.ref('ct_list_price.report_list_price').report_action(self, data=data)


class ReportListPrice(models.AbstractModel):
    _name = "report.ct_list_price.ct_list_price_card_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        dataset=[]
        price_list = self.env['product.pricelist'].browse(int(data['form']['list_price_id']))
        if str(data['form']['type'])=='categ':
            if int(data['form']['bool_exist'])==0:
                products=self.env['product.product'].search([
                    ('categ_id','=', int(data['form']['value_search']))
                ], order="name asc")
            else:
                products = self.env['product.product'].search([
                    ('categ_id', '=', int(data['form']['value_search'])),
                    ('qty_available','>',0)
                ], order="name asc")
        else:
            if int(data['form']['bool_exist'])==0:
                products=self.env['product.product'].search([
                    ('brand_id','=', int(data['form']['value_search']))
                ], order="name asc")
            else:
                products = self.env['product.product'].search([
                    ('brand_id', '=', int(data['form']['value_search'])),
                    ('qty_available','>',0)
                ], order="name asc")

        for p in products:
            dataset.append({
                'sku': p.default_code,
                'name': p.name.rjust(len(p.name)-50, " ") if len(p.name)<50 else p.name[0:49],
                'imagen': p.image_1920,
                'pu': round(price_list.get_product_price(p, 1, None, ),2),
                'emin': p.emin
            })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_publish': time.strftime('%Y-%m-%d'),
            'company': self.env.user.company_id,

            'user': self.env.user,
            'docs': dataset
        }


class dialogContainerCategory(models.TransientModel):
    _name='ct.list.price.dialog.container.category'
    container_category_id = fields.Many2one(
        'ct.list.price.container.category',
        string='Lista de Precios a Seleccionar',
        ondelete='restrict',
        index=True)
    list_price_id = fields.Many2one(
        'product.pricelist',
        string='Tarifa',
        ondelete='restrict',
        required=True,
        index=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'list_id': int(self.container_category_id.id),
                'list_price_id': int(self.list_price_id.id)
            },
        }
        return self.env.ref('ct_list_price.report_list_price_container').report_action(self, data=data)


class ReportListPriceContainerCategory(models.AbstractModel):
    _name = "report.ct_list_price.ct_list_price_card_container_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        dataset=[]
        dataset_category=[]
        price_list = self.env['product.pricelist'].browse(int(data['form']['list_price_id']))
        container=self.env['ct.list.price.container.category'].browse(int(data['form']['list_id']))
        for c in container.categ_childs_ids:
            dataset_category.append({
                'id': c.id,
                'name': c.name
            })
        products=self.env['product.product'].search([
            ('categ_id', 'in', container.categ_childs_ids.ids)
        ])

        for p in products:
            dataset.append({
                'sku': p.default_code,
                'name': p.name.rjust(len(p.name)-50, " ") if len(p.name)<50 else p.name[0:49],
                'imagen': p.image_1920,
                'pu': round(price_list.get_product_price(p, 1, None, ),2),
                'categ_id': p.categ_id.id,
                'emin': p.emin
            })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_publish': time.strftime('%Y-%m-%d'),
            'company': self.env.user.company_id,
            'user': self.env.user,
            'dataset_categ': dataset_category,
            'docs': dataset
        }






