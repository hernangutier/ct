from odoo import fields, models, api


class CreateInvAdjustAuditDialog(models.TransientModel):
    _name = 'create.inv.adjust.audit.dialog'
    _description = 'Description'

    name = fields.Char()
