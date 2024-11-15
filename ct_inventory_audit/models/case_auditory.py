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
    motivo=fields.Text('Descripcion del Caso', default='S/I')
    note=fields.Text('Notas')
    #---- Producto que reporta la Incidencia ---
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        required=True,
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
        adjust=self.env['stock.inventory'].search([
            ('audit_id','=',self.id)
        ],limit=1)
        #raise UserError(adjust.id)
        if len(adjust)>=1:
            form_view_id = self.env.ref('stock.view_inventory_form').id
            domain = [('id', '=', int(adjust.id))]
            context = { 'default_id': adjust.id, 'create': 0,
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
        #--- llamada al dialogo para crear ajuste de inventario
        self.ensure_one()
        context = {
            'default_case_audit_id': self.id,
            'default_date_accounting': fields.Date.today(),
        }
        # ----- Retornamos la Vista ----
        action = {
            'name': _('Procesar Caso'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'create.inv.adjust.audit.dialog',
            'context': context,
        }
        return action

    #--- Cancelar el Caso ---
    def action_cancel(self):
        self.ensure_one()
        self.write({
            'state': 'cancel'
        })
        return self


