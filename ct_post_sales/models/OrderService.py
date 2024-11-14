import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_



#------------------------------------------------------------------
#
#     Tabulador
#
#------------------------------------------------------------------

class Tabulator(models.Model):
    _name="ct.post.sales.tabulator"
    name=fields.Char('Ref.', default="/")
    denominacion=fields.Char('Descripcion', required=True)
    value=fields.Float('Valor a Pagar')
    # ---- Clasificador -------------
    tabulator_clas_id = fields.Many2one(
        'ct.post.sales.tabulator.clas',
        string='Clasificador',
        ondelete='restrict',
        index=True)

    @api.model
    def create(self, vals):
        if "name" not in vals or vals["name"] == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('tb')
        tabulator = super(Tabulator, self).create(vals)
        return tabulator

    #----- Sobreescribimos los Metodos de Crear para Asignar la Ref de Tabulador ---


class TabulatorClas(models.Model):
    _name="ct.post.sales.tabulator.clas"
    name=fields.Char('Denominacion', required=True)




#------------------------------------------------------------------
#
#     Condiciones de los Equipos
#
#------------------------------------------------------------------
class EquipmentConditions(models.Model):
        _name="ct.p.s.equipment.conditions"
        name=fields.Char('Condicion de Equipo',require=True)


#------------------------------------------------------------------
#
#     Ordenes de Servicios en Garantias
#
#------------------------------------------------------------------
class OrderService(models.Model):
    _name="ct.p.s.order.service"
    name=fields.Char("# Control", default="Nuevo")
    # ---- Distribuidor -------------
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura/Origen',
        ondelete='restrict',
        index=True)
    #----- Para Determinar la Compania ---
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True, required=True)

    is_payment_comission=fields.Boolean('Comision->Pagada (S/N)', default=False)

    category_order = fields.Selection([
        ('client', 'Cliente Final'),
        ('alia', 'Aliado Comercial'),  # ---- Habiulitar Solicitudes de Repuestros
    ], string='Clasificacion Caso', copy=False, index=True, default='client', store=True, required=True)
    
    info_invoice=fields.Char('Inforamacion de Factura Cliente Final')

    equipment_conditions_ids = fields.Many2many(
        'ct.p.s.equipment.conditions', string='Condiciones del Equipo')

    type=fields.Selection([
        ('new', 'Caso Nuevo'),
        ('rein', 'Caso Reincidente'), #---- Habiulitar Solicitudes de Repuestros
    ], string='Tipo', copy=False, index=True, default='new', store=True, required=True)

    #------ Fecha de Reporte --------------------------------
    date_report=fields.Date('Fecha Reportada', required=True)
    # ------ Fecha de Cierre --------------------------------
    date_report_close = fields.Date('Fecha de Cierre')

    #---- Distribuidor -------------
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string='Distribuidor/Aliado Comercial',
        ondelete='restrict',
        index=True)

    #----- Centro de Servicio ------
    service_id = fields.Many2one(
        'res.partner',
        string='Centro de Servicio',
        required=True,
        ondelete='restrict',
        domain="[('is_centre_service','=',True)]",
        context="{'search_default_supplier': 1,'res_partner_search_mode': 'supplier', 'default_is_company': True, 'default_supplier_rank': 1,'is_service_tecnical': True }",
        index=True)

    # ----- Mecanico Asignado  ------
    mechanical_id = fields.Many2one(
        'res.partner',
        string='Mecanico Asignado',
        ondelete='restrict',
        domain="[('is_mechanical','=',True)]",
        context="{'search_default_supplier': 1,'res_partner_search_mode': 'supplier', 'default_is_company': True, 'default_supplier_rank': 1,'is_mechanical': True }",
        index=True)
    #----- Producto o Equipo a Registrar por Garantias
    product_id = fields.Many2one(
        'product.product',
        required=True,
        string='Equipo',
        ondelete='restrict',
        domain="[('apply_type','=','eq')]",
        index=True)

    is_fail_origin=fields.Boolean('Desperfecto de Fabrica S/N', default=False)
    # ---- Distribuidor -------------
    contact_id = fields.Many2one(
        'res.partner',
        string='Cliente/Final',
        ondelete='restrict',
        index=True)
    #---------- Estado de la Transaccion ---------------------
    state = fields.Selection([
        ('serv', 'en Centro de Servicio'),
        ('rev', 'en Revision'), #---- Habiulitar Solicitudes de Repuestros
        ('dev', 'en Reparacion'),
        ('wait', 'en Espera de Entrega al Cliente'),
        ('done', 'Finalizada'),
    ], string='Estado', copy=False, index=True, default='serv', store=True, required=True)


    #---- Orden de Servicio Reincidencias -----
    os_reinv_id = fields.Many2one(
        'ct.p.s.order.service',
        string='Order Padre',
        ondelete='restrict',
        index=True)

    #---------- Descripcion de la Falla ----------------------
    information_fail=fields.Text('Descripcion de la Falla', required=True)
    # ---------- Diagnosticos y Resultados  ----------------------
    diagnostic_note = fields.Text('Diagnostico')
    #---------- Costo estimado del Servicio ------------------
    amount_cost_service=fields.Float('Costo Total del Servicio')
    amount_cost_tabulator=fields.Float('Costo Mano de Obra', compute="_get_cost")

    def _get_cost(self):
        for l in self:
            acu = 0
            #----- Acumulamos los Costos de Tabulacion Registrada ---
            cost=self.env['ct.p.s.cost.tabulator.order.service'].search([
                ('order_id','=',l.id)
            ])
            for c in cost:
                acu+=c.value
            l.amount_cost_tabulator=acu

    @api.model
    def create(self,vals):
        if "name" not in vals or vals["name"] == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code('os')
        order_service = super(OrderService, self).create(vals)
        return order_service


    #------- Verificacion de Tranferescias Abiertas ---
    def is_transfer_open(self, type):
        transfers = self.env['stock.picking'].search([
            ('os_id', '=', self.id),
            ('picking_type_id', '=', type),
            ('state', 'not in', ('done', 'cancel'))
        ])
        if len(transfers)>0:
            return True
        return False

    #--- Indica si hay Registros de costos de Tabulacion por Mano de Obra
    def is_records_cost_tabulator(self):
        count=self.env['ct.p.s.cost.tabulator.order.service'].search([(
            'order_id', '=', self.id
        )])
        if len(count)>1:
            return True
        return False

    #--------- Conteo de las Trasferencias Registradas --
    def transfer_count(self,type):
        transfers = self.env['stock.picking'].search([
            ('os_id', '=', self.id),
            ('picking_type_id', '=', type),
        ])
        return len(transfers)

    #----- Solicitud de Transferencias de Inventario ----
    def action_view_transfers(self):
        self.ensure_one()
        #-------- Verificamos si hay Transferencias
        if self.state=='done' or self.is_transfer_open(5):
            context = {'default_os_id': self.id, 'default_origin': self.name, 'edit': 1, 'create': 0,
                           'default_picking_type_id': 5,
                           'default_partner_id': self.partner_id.id}
        else:
            context = {'default_os_id': self.id, 'default_origin': self.name, 'default_picking_type_id': 5,
                       'default_partner_id': self.partner_id.id}

        domain = [('os_id', '=', self.id), ('picking_type_id', '=', 5)]
        tree_view_id = self.env.ref(
            'ct_post_sales.view_ct_post_sales_stock_picking_transfer_tree').id
        form_view_id = self.env.ref(
            'ct_post_sales.view_ct_post_sales_stock_picking_form').id

        action = {
            'name': _('Transferencias de Repuestos'),
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
            'view_id': tree_view_id if self.transfer_count(5)>0 else form_view_id,
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'context': context,
            'domain': domain,
        }
        return action

    #---- Descargar Inventario para uso de la Garantia
    def action_view_picking_out(self):
        self.ensure_one()
        # -------- Verificamos si hay Transferencias
        if self.state == 'done' or self.is_transfer_open(7):
            context = {'default_os_id': self.id, 'default_origin': self.name, 'edit': 1, 'create': 0,
                       'default_picking_type_id': 7,
                       'default_partner_id': self.partner_id.id}
        else:
            context = {'default_os_id': self.id, 'default_origin': self.name, 'default_picking_type_id': 7,
                       'default_partner_id': self.partner_id.id}

        domain = [('os_id', '=', self.id), ('picking_type_id', '=', 7)]
        tree_view_id = self.env.ref(
            'ct_post_sales.view_ct_post_sales_stock_picking_transfer_tree').id
        form_view_id = self.env.ref(
            'ct_post_sales.view_ct_post_sales_stock_picking_form').id

        action = {
            'name': _('Repuestos a Implementar'),
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_id': tree_view_id ,
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'context': context,
            'domain': domain,
        }
        return action

    #------ Vista para Registrar los Costos de Servicio por Mano de Ogra segun Tabulador --
    def action_view_cost_tabulator(self):
        self.ensure_one()
        # -------- Verificamos si hay Transferencias
        if self.state == 'done':
            context = {'default_order_id': self.id, 'default_tabulator_clas_id': self.product_id.product_tmpl_id.tabulator_clas_id.id, 'edit': 1, 'create': 0}
        else:
            context = {'default_order_id': self.id, 'default_tabulator_clas_id': self.product_id.product_tmpl_id.tabulator_clas_id.id, 'create': 1, 'edit': 1, 'delete': 1}

        domain = [('order_id', '=', self.id)]
        tree_view_id = self.env.ref(
            'ct_post_sales.view_ct_post_sales_tabulator_order_tree').id
        action = {
            'name': _('Costos Mano de Obra (Tabulador)'),
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_id': tree_view_id,
            'view_mode': 'tree,form',
            'res_model': 'ct.p.s.cost.tabulator.order.service',
            'context': context,
            'domain': domain,
        }
        return action


    # ------ Vista para Registrar los Costos de Servicio por Mano de Ogra segun Tabulador --

    def action_view_order_child(self):
        os_childs=self.search([('os_reinv_id','=', self.id)])
        if len(os_childs)>0:
            domain = [('id', '=', os_childs.ids)]
            context = {'create': 0,
                       'edit': 1, 'delete': 0}
            action = {
                'name': _('Ordenes Reincidentes'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'ct.p.s.order.service',
                'context': context,
                'domain': domain,
            }
            return action
        else:
            raise UserError('No Existen Ordenes de Reincidencia!')

    #-------------------------------------------------------------
    #   Acciones y Command de la Interfaz Grafica
    #
    #
    #-------------------------------------------------------------

    #----- En Espera de Retiro al Cliente ---------------
    def action_send_wait_client(self):
        if not len(self.diagnostic_note) > 11: raise UserError('Debe indicar un Informe Diganistico...')
        self.ensure_one()
        self.write({
            'state': 'wait'
        })
        return self

    #------ Enviar a Revision ----
    def action_send_to_rev(self):
        if not self.mechanical_id: raise UserError('Debe seleccionar un Mecanico...')
        self.ensure_one()
        self._check_in_calc()
        self.write({
            'state': 'rev'
        })

    def _check_in_calc(self):
        self.ensure_one()
        line = self.env['ct.post.sales.commissions.line'].search([('os_id', '=', self.id)])
        if len(line) >= 1:
            raise UserError("La orden de servicio se encuentra en calculo, no se puede concluir la operacion.")



    # ------ Enviar a Reparacion ----
    def action_send_to_repair(self):

        if not len(self.diagnostic_note) > 11: raise UserError('Debe indicar un Informe Diganistico...')
        self.ensure_one()
        self._check_in_calc()
        self.write({
            'state': 'dev'
        })


    # ------ Cerrar la Orden de Servicio  ----
    def action_send_close(self):
        self.ensure_one()
        if not self.date_report_close:
            raise UserError('Debe indicar una fecha de cierre de la Orden de Servicio!')
        if not self.diagnostic_note:
            raise UserError('Debe indicar un diagnostico de la Orden de Servicio!')
        #----- Verificamos si hay Operaciones Abiertas --------
        if self.is_transfer_open(5): raise UserError('Tienes Trasnferencias de Inventario Pendientes...')
        if self.is_transfer_open(7): raise UserError('Tienes Descargas de Inventario Pendientes...')

        self.write({
            'state': 'done'
        })
        return self

    def action_create_recidivism(self):
        context={
            'default_os_reinv_id'     : self.id if self.type=='new' else self.os_reinv_id.id,
            'default_product_id'      : self.product_id.id,
            'default_date_report'     : fields.Date.today(),
            'default_type'            : 'rein' ,
            'default_category_order'  : self.category_order,
            'default_partner_id'      : self.partner_id.id,
            'default_contact_id'      : self.contact_id.id,
            'default_service_id'      : self.service_id.id
        }
        #----- Retornamos la Vista ----
        action = {
            'name'       : _('Orden Reincidente'),
            'type'       : 'ir.actions.act_window',
            'view_mode'  : 'form',
            'res_model'  : 'ct.p.s.order.service',
            'context'    : context,
        }
        return action

class CostTabulatorOrderService(models.Model):
    _name="ct.p.s.cost.tabulator.order.service"
    #---- Orden de Servicio ------------
    order_id=fields.Many2one(
        'ct.p.s.order.service',
        string='Orden de Servicio',
        ondelete='restrict',
        index=True)

    # ---- Tabulador Items -------------
    tabulator_clas_id = fields.Many2one(
        'ct.post.sales.tabulator.clas',
        string='Clasificador',
        ondelete='restrict',
        index=True)

    tabulator_id = fields.Many2one(
        'ct.post.sales.tabulator',
        string='Items Tabulador',
        ondelete='restrict',
        index=True)

    descripcion= fields.Char(related='tabulator_id.denominacion',copy=False, readonly=True, store=True)



    value=fields.Float('Cost. S/Tabulador')

    @api.onchange('tabulator_id')
    def onchange_tabulator_id(self):
        self.value=self.tabulator_id.value


    #------ Sobreescribir el Create para evitar Duplicar Costos de Mano de Obra -----
    @api.constrains('tabulator_id')
    def _check_tabulator_id_key(self):
        for l in self:
            count=l.env['ct.p.s.cost.tabulator.order.service'].search([
                ('order_id','=', self.order_id.id),
                ('tabulator_id','=', self.tabulator_id.id)
            ])
            if len(count)>=2:
                raise ValidationError('Esta Intentando registrar dos servicios iguales...')