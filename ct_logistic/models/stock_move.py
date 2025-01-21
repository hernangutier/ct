from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'
    qty_verified = fields.Integer('Cnt. verificada', default=0)