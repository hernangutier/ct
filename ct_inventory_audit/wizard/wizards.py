from odoo import fields, models, api


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
                new_move=self.env['stock.inventory'].browse(int(self.id))
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


