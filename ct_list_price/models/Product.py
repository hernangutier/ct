import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Campos adicionales de forma para product.template
#
#--------------------------------------------------------------------

class ProductTemplate(models.Model):
    _inherit="product.template"

    name_short=fields.Char('Nombre Corto', compute="_get_name_short")


    def _get_name_short(self):
            if len(self.name)>60:
               return self.name[1:59]
            else:
                return self.name


class ProductCategory(models.Model):
    _inherit="product.category"
    #---- Campo Posicion en la Lista
    list_positions=fields.Integer('Posicion en Lista de Precios', default=0)
    active_list_price=fields.Boolean('Activar P/Lista de Precios', default=True)


#---- Clase para Configurar Productos en Pre-Venta ---
class ProductPreSale(models.Model):
    _name="ct.list.price.product.pre.sale"

    list_positions = fields.Integer('Posicion en Lista de Precios', default=0)
    # ---- Producto que reporta la Incidencia ---
    product_id = fields.Many2one(
        'product.template',
        string='Producto',
        ondelete='restrict',
        required=True,
        index=True)






