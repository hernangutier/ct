import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class CommisionsRelations(models.AbstracModel):
    _name="report.ct.post.sales.commissions.relations"


    def _get_report_values(self,docids,data=None):
        report_obj=self.env['ir.action.report']
        report=report_obj._get_report_from_name('ct_pots_sales.commissions_pdf_2100')
        doc=self.env['ct.post.sales.commisions'].browse(docids)


