import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Reglas de Penalizacion
#
#--------------------------------------------------------------------

class RulesPolice(models.Model):
    _name="ct.sale.power.rules.police"
    lmin = fields.Integer('A Partir de (dias) post Vencimiento', required=True,
                          help="Indica que a partir de N dias aplicara la regla")
    percent_police = fields.Float('% de Penalización', required=True,
                                  help="% aplicado para penalizar sobre el monto calculado generar la comision ajustada")

    @api.constrains('lmin')
    def check_lmin(self):
        list = self.env['ct.sale.power.rules.police'].search([('lmin', '=', self.lmin)])
        if len(list) > 1:
            raise ValidationError('Esta Regla ya esta definida...')
     