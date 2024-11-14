import time
import math
import json
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class DeclaracionReport(models.AbstractModel):
    _name="report.ct_cobranza.ct_pdf_report_1008"

    def _get_report_values(self,docids,data=None):


        report_obj=self.env['ir.actions.report']
        report=report_obj._get_report_from_name('ct_cobranza.ct_pdf_report_1008')
        return {
            'doc_ids': docids,
            'doc_model' : self.env['ct.cobranza.payment.efective.control'],
            'docs': self.env['ct.cobranza.payment.efective.control'].browse(docids),
            'company': self.env.user.company_id,
        }