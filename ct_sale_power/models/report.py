import time
import math
import json
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class CommisionsReport(models.AbstractModel):
    _name="report.ct_sale_power.ct_pdf_report_1200"

    def _get_report_values(self,docids,data=None):


        report_obj=self.env['ir.actions.report']
        report=report_obj._get_report_from_name('ct_sale_power.ct_pdf_report_1200')
        return {
            'doc_ids': docids,
            'doc_model' : self.env['ct.sale.power.commissions'],
            'docs': self.env['ct.sale.power.commissions'].browse(docids),
            'company': self.env.user.company_id,
        }