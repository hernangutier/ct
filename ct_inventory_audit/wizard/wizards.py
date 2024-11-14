from odoo import fields, models, api


class CreateInvAdjustAuditDialog(models.TransientModel):
    _name = 'create.inv.adjust.audit.dialog'
    _description = 'Description'
    case_audit_id = fields.Many2one(
        'ct.inventory.audit.case.audit',
        string='Caso de Auditoria',
        ondelete='restrict',
        required=True,
        index=True)
    date_accounting=fields.Date('Fecha de Contabilizacion', required=True)
    value_count=fields.Integer('Conteo Final',required=True)

    #---- Post para Realizar Ajuste de Inventario Automatizado con
    #---- Referencia a la Operacion de Auditoria --
    def post(self):
        line=[]
        location_ids=[]
        #---- Creamos la Linea de Inventario
        vals = (0, 0, {
            'product_id': self.product_id.id,
            'product_qty': self.value_count,
            'location_id': self.case_audit_id.location_id.id,
        })
        line.append(vals)
        location_ids.append(self.case_audit_id.location_id.id)


        #---- Creamos el Registro Principal
        move=self.env['stock.inventory']
        move.create({
            'name': self.case_audit_id.name,
            'location_ids': [(6,0,self.case_audit_id.id)],
            'product_ids': [(6,0,self.product_id.id)],
            'motivo': 'Ajuste de Inventario Segun Auditoria # ' + self.case_audit_id.name + ' de fecha: ' + self.date_accounting
        })
        #---- Validamos la Operacion
        pass
