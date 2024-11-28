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
#    Modelo Commons par Reportes de Listado
#
#
# ----------------------------------------------------------

class Commons(models.TransientModel):
    _name = "ct.commons.wz.commons"
    title = fields.Char()

    date_init = fields.Date('Desde')
    date_end = fields.Date('Hasta')
    date_print_report = fields.Date()

    #--- Campos para Historicos de Lista de Precios ---
    with_qty=fields.Boolean('Con Existencias', default=True)
    is_public_list=fields.Boolean('Publicado en Lista', default=True)
    list_price_id = fields.Many2one(
        'product.pricelist',
        string='Tarifa',
        ondelete='restrict',
        required=False,
        index=True)
    #---------------------------------------------------

    def check_date(self):
        if self.date_init>=self.date_end:
            raise UserError('Rango de fechas incorrecto!')

    def get_report(self):
        pass
        #self.check_date()

