import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_

class AccountMove(models.Model):
    _inherit="account.move"

    def do_print_invoice(self):
        return self.env.ref('action_account_move_note_report_pdf').report_action(self)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def do_print_picking(self):
        return self.env.ref('action_stock_picking_report_pdf').report_action(self)
