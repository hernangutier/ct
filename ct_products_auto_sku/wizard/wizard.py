import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ProductTraslateCategoryForm(models.TransientModel):
    _name="ct.product.traslate.category"

    #----- Categoria a Recibir los Productos ----
    categ_id = fields.Many2one(
        'product.category',
        string='Categora a Recibir Traslado...',
        ondelete='restrict',
        required=True,
        index=True)
    #------- Este Metodo Transladamos de Categoria --
    def post_traslate(self):
        products=self.env['product.template'].search([(
            'id', 'in', self.env.context.get('active_ids')
        )], order='name asc')
        #---- Actualizamos el SKu Auto generado por la Categoria ---
        sequence = self.env["ir.sequence"].get_category_sequence_id(self.categ_id)
        for p in products:
            p.write({
                'default_code': sequence.next_by_id(),
                'categ_id': self.categ_id.id
            })
        return  products
