from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class CreateInvAdjustAuditDialog(models.TransientModel):
    _name = 'create.inv.adjust.audit.dialog'
    _description = 'Description'

    create_adjust=fields.Boolean('Crear Ajuste (S/N)', default=True)
    case_audit_id = fields.Many2one(
        'ct.inventory.audit.case.audit',
        string='Caso de Auditoria',
        ondelete='restrict',
        index=True)
    date_accounting=fields.Date('Fecha de Contabilizacion')
    value_count=fields.Integer('Conteo Final',default=0)
    product_name=fields.Char('Producto', related='case_audit_id.product_id.display_name', copy=False, readonly=True, store=True)
    product_qty_available=fields.Float('Qty. Teorica', related='case_audit_id.product_id.qty_available', copy=False, readonly=True, store=True )
    difference_qty=fields.Float('Diferencia a Registrar', computed="_get_diff")

    #----- Calcular la Diferencia a Registrar ---
    @api.onchange('value_count')
    def _get_diff(self):
        self.ensure_one()
        self.difference_qty=self.product_qty_available-self.value_count
    #---- Post para Realizar Ajuste de Inventario Automatizado con
    #---- Referencia a la Operacion de Auditoria --
    def post(self):
        if self.create_adjust:
                audit_id=self.case_audit_id
                line_ids=[]
                location_ids=[]
                #---- Creamos la Linea de Inventario
                vals = (0, 0, {
                    'product_id': self.case_audit_id.product_id.id,
                    'product_qty': self.value_count,
                    'location_id': self.case_audit_id.location_id.id,
                })
                line_ids.append(vals)
                location_ids.append(self.case_audit_id.location_id.id)
                products_ids=[]
                products_ids.append(self.case_audit_id.product_id.id)

                #---- Creamos el Registro Principal
                move=self.env['stock.inventory']
                move.create({
                            'name': self.case_audit_id.name,
                            'state': 'confirm',
                            'audit_id': self.case_audit_id.id,
                            'location_ids': [(6,0,location_ids)],
                            'product_ids': [(6,0,products_ids)],
                            'line_ids': line_ids,
                            'motivo': 'Ajuste de Inventario Segun Auditoria # ' + self.case_audit_id.name + ' de fecha: ' + str(self.date_accounting)
                        })
                new_move=self.env['stock.inventory'].search([
                    ('audit_id','=', audit_id.id)
                ], limit=1)
                # ---- Validamos la Operacion

                new_move.action_validate()
                #new_case=self.env['ct.inventory.audit.case.audit'].browse(int(self.audit_id.id))
                audit_id.write({
                    'state': 'done',
                    'date_done': fields.Date.today(),
                })
        else:
            self.case_audit_id.write({
                'state': 'done',
                'date_done': fields.Date.today()
            })


