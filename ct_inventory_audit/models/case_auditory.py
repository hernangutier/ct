from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class CaseAuditory(models.Model):
    _name = 'ct.inventory.audit.case.audit'
    _description = 'Control de Auditorias'

    name = fields.Char('#Caso:', default='/')
    motivo=fields.Text('Descripcion del Caso', default='S/I')
    note=fields.Text('Notas')
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        required=True,
        index=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Almacen',
        ondelete='restrict',
        required=True,
        index=True)


    #---- Cantidad Reportada Por el Almacen ---
    qty_value=fields.Integer('Cantidad Reportada', help='Catidad Reportada', default=0)
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
    ], string='Estado', copy=False, index=True, default='new', store=True, required=True)

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
        pass
    #---- Crear Ajuste de Inventario ----
    def create_adjust(self):
        pass

