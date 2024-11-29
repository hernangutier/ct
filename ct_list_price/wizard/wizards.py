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

class ProductsListPriceDialog(models.TransientModel):
    _name = 'ct.list.price.dialog.container.category'
    _inherit="ct.commons.wz.commons"
    _description = 'Dialogo para Generar la Lista de Precios'

    # ----- Todos los Grupo o General  --------
    type_mod = fields.Boolean('General/Grupo', default=False)

    container_category_id = fields.Many2one(
        'ct.list.price.container.category',
        string='Lista de Precios a Seleccionar',
        ondelete='restrict',
        index=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'list_id': int(self.container_category_id.id),
                'list_price_id': int(self.list_price_id.id),
                'with_qty': self.with_qty,
                'type_mod': self.type_mod
            },
        }
        return self.env.ref('ct_list_price.report_list_price_container').report_action(self, data=data)



class ReportListPriceContainerCategory(models.AbstractModel):
    _name = "report.ct_list_price.ct_list_price_card_container_pdf"



    @api.model
    def _get_report_values(self, docids, data=None):
        #--- Agregar Logica para Manejar dos Modos de reportes ---


        dataset=[]
        dataset_category=[]
        price_list = self.env['product.pricelist'].browse(int(data['form']['list_price_id']))
        #--- Function Interna para Crear Registros
        def load_dataset():
            dataset.append({
                'sku': p.default_code,
                'name': p.name.rjust(len(p.name) - 50, " ") if len(p.name) < 50 else p.name[0:49],
                'imagen': p.image_1920,
                'pu': round(price_list.get_product_price(p, 1, None, ), 2),
                'categ_id': p.categ_id.id,
                'emin': p.emin
            })
        if data['form']['type_mod']==True:
            container=self.env['ct.list.price.container.category'].browse(int(data['form']['list_id']))
            for c in container.categ_childs_ids.sorted(key=lambda x: x.list_positions):
                dataset_category.append({
                    'id': c.id,
                    'name': c.name,
                })
            products=self.env['product.product'].search(['&',
                ('categ_id', 'in', container.categ_childs_ids.ids),
                ('type','=','product'),
                ('sale_ok','=',True)
            ], order='name asc')
        else:
            container=self.env['product.category'].search([
                ('parent_id','!=',None)
            ], order='name')
            for c in container:
                dataset_category.append({
                    'id': c.id,
                    'name': c.name,
                })
            products = self.env['product.product'].search(['&',
                                                           ('categ_id', 'in', container.ids),
                                                           ('type', '=', 'product'),
                                                           ('sale_ok', '=', True)
                                                           ], order='name asc')

        for p in products:
          if data['form']['with_qty']==True:
            if p.qty_available>0:
               load_dataset()
          else:
               load_dataset()

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_publish': time.strftime('%Y-%m-%d'),
            'company_id': self.env.user.company_id,
            'user': self.env.user,
            'dataset_categ': dataset_category,
            'docs': dataset
        }

