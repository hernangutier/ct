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

    day_due= fields.Integer('Dias/Retraso', compute="_get_day_due")

    #--- Este Metodo Calcula los dias de Retraso ----
    def _get_day_due(self):
        for i in self:
            if i.date_due_delivered:
                diff= int((fields.Date.today() - i.date_due_delivered).days)
                if diff > 0:
                    i.day_due=diff
                else:
                    i.day_due=0
            else:
                i.day_due=0

