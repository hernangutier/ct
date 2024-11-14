import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#     Modificacion del Registro de Pagos
#
#--------------------------------------------------------------------

class AccountPayment(models.Model):
    _inherit="account.payment"

    #--------- Info de Facturas Conciliadas -----
    invoice_reconciled_info=fields.Char('Ref/Afectadas', compute="_compute_ref_reconciled")

    def _compute_ref_reconciled(self):
        data=''
        for inv in self.reconciled_invoice_ids:
            data+=inv.name + ','
        if len(data)>0:
           data=data[:len(data)-1]
        self.invoice_reconciled_info=data
