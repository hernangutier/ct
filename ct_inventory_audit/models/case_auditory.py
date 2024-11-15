from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class CaseAuditory(models.Model):
    _name = 'ct.inventory.audit.case.audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Control de Auditorias'

    name = fields.Char('#Caso:', default='/')
    create_adjust = fields.Boolean('Crear Ajuste (S/N)', default=True)
    motivo=fields.Text('Descripcion del Caso', default='S/I')
    note=fields.Text('Notas')
    #---- Producto que reporta la Incidencia ---
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        required=True,
        index=True)

    move_id = fields.Many2one(
        'stock.inventory',
        string='Ajuste de Inventario',
        ondelete='restrict',
        index=True)

    #--- Almacen donde se reporto la incidencia ---
    location_id = fields.Many2one(
        'stock.location',
        string='Almacen',
        ondelete='restrict',
        required=True,
        index=True)

    #--- Fecha de la Incidencia ----
    date=fields.Date('Fecha Incidencia')

    date_done=fields.Date('Fecha de Finalizacion')

    type= fields.Selection([
        ('falt', 'Faltante'),
        ('sob', 'Sobrante'),  # ---- Habiulitar Solicitudes de Repuestros
        ('det', 'Deteriorado'),
        ('otro', 'Otro Especifique'),
    ], string='Tipo Caso', copy=False, index=True, default='falt', store=True, required=True)

    specific=fields.Text('Especifique el Caso...', help="Especifique la Incidencia del Caso...", required=True)

    state = fields.Selection([
        ('new', 'Nuevo'),
        ('rev', 'en Revision'),  # ---- Habiulitar Solicitudes de Repuestros
        ('done', 'Terminado'),
        ('cancel', 'Cancelado'),
    ], string='Estado', copy=False, index=True, tracking=3, default='new', store=True, required=True)

    value_count = fields.Integer('Conteo Final', default=0)

    product_qty_available = fields.Float('Qty. Teorica', related='product_id.qty_available', copy=False,
                                         readonly=True, store=True)
    difference_qty = fields.Float('Diferencia a Registrar', computed="_get_diff")

    @api.model
    def create(self,vals):
        if "name" not in vals or vals["name"] == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('au')
        case_auditory = super(CaseAuditory, self).create(vals)
        return case_auditory

    visibility=fields.Boolean(default=False, compute="get_visibility")


    def get_visibility(self):
        self.ensure_one()
        #--- Consultamos los Ajustes de Inventario
        adjustCount=self.env['stock.inventory'].search([
            ('audit_id','=',self.id)
        ])
        if len(adjustCount)>0:
            self.visibility=True
        else:
            self.visibility=False
    #---- Vista de Ajustes de Inventarios Relacinadas con la Auditoria
    def action_view_related_inventory_adjust_loads(self):
        self.ensure_one()
        #--- Consultamos para ver si hay ahuste de Inventario aplicado --
        if len(self.move_id)>=1:
            form_view_id = self.env.ref('stock.view_inventory_form').id
            domain = [('id', '=', int(self.move_id))]
            context = { 'default_id': self.move_id, 'create': 0,
                       'edit': 0, 'delete': 0}

            action = {
                'name'      : _('Ajuste Aplicado'),
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'tree,form',
                'res_model' : 'stock.inventory',
                'context'   : context,
                'domain'    : domain,
            }
            return action
        return UserError('No hay Ajustes Registrados...')



    #---- Enviar a Revision el Estado del Caso
    def action_send_rev(self):
        self.ensure_one()
        self.state='rev'
        return self
    #---- Crear Ajuste de Inventario ----
    def create_adjust(self):
        self.ensure_one()
        if self.create_adjust:
                audit_id=self.id
                line_ids=[]
                location_ids=[]
                #---- Creamos la Linea de Inventario
                vals = (0, 0, {
                    'product_id': self.product_id.id,
                    'product_qty': self.value_count,
                    'location_id': self.location_id.id,
                })
                line_ids.append(vals)
                location_ids.append(self.location_id.id)
                products_ids=[]
                products_ids.append(self.product_id.id)

                #---- Creamos el Registro Principal
                move=self.env['stock.inventory']
                move.create({
                            'name': 'AI/' + self.name,
                            'state': 'confirm',
                            'location_ids': [(6,0,location_ids)],
                            'product_ids': [(6,0,products_ids)],
                            'line_ids': line_ids,
                            'motivo': 'Ajuste de Inventario Segun Auditoria # ' + self.case_audit_id.name + ' de fecha: ' + str(self.date_accounting)
                        })
                # ---- Validamos la Operacion
                move.action_validate()
                #new_case=self.env['ct.inventory.audit.case.audit'].browse(int(self.audit_id.id))
                audit_id.write({
                    'move_id': move.id,
                    'state': 'done',
                    'date_done': fields.Date.today(),
                })
        else:
            self.write({
                'state': 'done',
                'date_done': fields.Date.today()
            })


    #--- Cancelar el Caso ---
    def action_cancel(self):
        self.ensure_one()
        self.write({
            'state': 'cancel'
        })
        return self


