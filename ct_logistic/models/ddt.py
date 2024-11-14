import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
#  Contenedor Logistico para administrar despacho de Pedidos
#
#--------------------------------------------------------------------

class Container(models.Model):
    _name="ct.logistic.container"
    _description="Container"
    #---- Numero de Control Logistico ------
    name=fields.Char('Numero/Control', require=True, default="Nuevo")
    #----- Tipo de Container ----------
    type = fields.Selection([
        ('ddt', 'Transporte/Empresa'),
        ('glp', 'en Empresa'),
        ('enc','Encomienda')
    ], string='Modalidad', copy=False, index=True, default='ddt', store=True, required=True)
    #------ Estado de Despacho
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('draft', 'en Carga'),
        ('transit', 'en Transito'),
        ('done', 'Procesado')
    ], string='Estado', copy=False, index=True, default='new', store=True, required=True)
    #------ Numero de Guia para las Encomiendas
    number=fields.Char('Numero/Guia', hepl="Numero de Guia para Encomiendas...")
    #---- Descripcion de la Ruta -----
    route=fields.Text('Descripcion de la Ruta')
    #--- Chofer Asignado -------------
    chofer_id = fields.Many2one(
        'res.partner',
        string='Chofer',
        ondelete='restrict',
        index=True)
    #----- Ayudante  -----------------
    ayudante_id = fields.Many2one(
        'res.partner',
        string='Auxiliar/Despacho',
        ondelete='restrict',
        index=True)
    #------ Vehiculo -----------------
    vehiculo_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehiculo',
        ondelete='restrict',
        index=True)

    supplier_service_id = fields.Many2one(
        'res.partner',
        string='Empresa',
        ondelete='restrict',
        index=True)
    #------ Fecha de Salida  -----
    date_init=fields.Date('Fecha de Salida')
    #---- Fecha de Cierre -----
    date_end=fields.Date('Fecha de Cierre')
    #----- Ordenes Cargadas ----
    order_ids = fields.Many2many(
        'sale.order',
        string='Pedidos Cargados'
    )

    def _get_lines_orders_consolidados(self):
        lines=  self.env['sale.order.line'].search([
            ('order_id', 'in', self.order_ids.ids)
        ])
        lines=lines.filtered(lambda x: x.product_id.departament_id.confirm_invoice_inmediate==True).sorted(key=lambda r: r.product_id.name)
        return lines

    def _get_group_lines(self):
        group=self.env['sale.order.line'].read_group(
             [('order_id', 'in', self.order_ids.ids)],
             ['product_id'],
             ['product_id']
            )

        data=[]
        for g in group:
            raise UserError(g['product_id'][0])
            data.append({
                'product': g.get(['product_id'][0])
            })
        return data


    #container_line_ids = fields.One2many('ct.logistic.container.line', 'container_id', string='Order Lines',
    #                              states={'done': [('readonly', True)],'draft': [('readonly', True)] },
    #                              copy=True,
    #                              auto_join=True)

    sale_order_count=fields.Integer('# Pedidos: ', compute="_calculate_retail", store=True)
    invoice_count=fields.Integer('#Facturas Vinculadas', compute="_calculate_retail")
    packing_count=fields.Integer('Total Bultos: ', compute="_calculate_retail")

    #---- Limpiar Pedidos de Container ---
    def clear(self):
       if len(self.order_ids)>0:
            self.order_ids=[(5,0,0)]
       else:
           raise UserError('No hay pedidos cargados...')

    def get_items_carga(self):
        data=[]
        data_result=[]
        for pedidos in self.order_ids:
            for lines in pedidos.order_line.filtered(lambda x: x.product_id.departament_id.confirm_invoice_inmediate==True and x.qty_delivered>0):
                    data.append({
                        'id': lines.product_id.id,
                        'product': lines.product_id.display_name,
                        'cnt': lines.qty_delivered,
                    })

        data.sort(key=lambda x: x['product'])
        product_group = ""
        value_count = 0
        for new_data in data:
            if new_data['product']!=product_group:
                #--------- Filtramos para contar
                value_name=new_data['product']
                value_id=new_data['id']
                for data_filter in  filter(lambda x: x['product']==new_data['product'],data):
                    value_count=value_count+data_filter['cnt']

                data_result.append({
                    'id': value_id,
                    'product':value_name,
                    'cnt':value_count
                })
            product_group=new_data['product']
            value_count=0
        return data_result

    @api.depends('order_ids')
    def _calculate_retail(self):
     #--- Calcula los Resumenes del Container ---
     invoice_count=0
     packing=0
     for s in self:
        s.sale_order_count = len(s.order_ids)
        for order in s.order_ids:
            packing+=order.packing_register
            invoice_count += len(order.invoice_ids.filtered(lambda x: x.state == 'posted'))
        s.invoice_count=invoice_count
        s.packing_count=packing


    def _check_lines_retrict(self ,vals):
      if vals["type"]=='ddt':
            raise UserError('Restrciciones...')



    @api.model
    def create(self,vals):
        #self._check_lines_retrict(vals)
        if "name" not in vals or vals["name"] == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code('ncl')
        container = super(Container, self).create(vals)
        for ltemp in self.order_ids:
            ltemp.write({
                'load': True,
                'info_delivered': container['name']
            })
        return container

    def write(self,vals):
        self.ensure_one()
        tmp = self.env['ct.logistic.container'].browse(self.id)
        for ltemp in tmp.order_ids:
            ltemp.write({
                'load': False,
                'info_delivered': ""
            })
        res = super(Container, self).write(vals)
        for ltemp in tmp.order_ids:
            ltemp.write({
                'load': True,
                'info_delivered': tmp.name
            })
        return res



    def check_container(self, status):
        if len(self.order_ids)==0:
            raise UserError('No hay Pedidos Cargados')
        for s in self.order_ids:
            if s.invoice_status!='invoiced':
                raise UserError('El pedido: ' + s.name + ' no esta Facturado...')
        if status=='done':
            for l in self.order_ids:
                for i in l.invoice_ids.filtered(lambda x: x.type=='out_invoice' and x.state=='posted'):
                    if i.state_delivered==False:
                        raise UserError('Debe cerrar la Factura #: ' + i.name + ' para Procesar el Container...')


    #----- Acciones ------
    #----- Enviar Container
    def send(self):
        self.check_container('transit')
        if not self.date_init:
            raise UserError('Debe Indicar una fecha de Salida...')
        self.write({
            'state': 'transit'
        })
    #----- Procesar Container ----
    def commit(self):
        self.check_container('done')
        self.write({
            'state': 'done'
        })
    def commit_with_date(self,date):
        self.check_container('done')
        self.write({
            'state': 'done',
            'date_end': date
        })
    #---- Inicia el Container para Poder Cargar Pedidos
    def initial(self):
        self.ensure_one()
        self.write({
            'state': 'draft'
        })

    def reopen(self):
        #--- debemos llamar a un Dialog para Controlar la Operacion
        self.write({
            'state': 'draft',
            'date_end': None
        })


    #--- Vista de Lineas de Pedidos
    def action_view_order_lines_products(self):
        self.ensure_one()
        domain = [('order_id', 'in', self.order_ids.ids)]
        action = {
            'name': _('Productos Solicitados'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'context': {'edit': 1, 'create': 0, 'group_by': 'product_id'},
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action

    #--- Mostrar Facturas Fiscales ----
    def action_view_related_container_invoice_fisacl_loads(self):
        self.ensure_one()
        if self.invoice_fiscal_ids():
            domain = [('account_move_id', 'in', self.invoice_fiscal_ids())]
            action = {
                    'name': _('Facturas Fiscales'),
                    'type': 'ir.actions.act_window',
                    'view_id': self.env.ref("ct_invoice_fiscal_imagen.view_ct_invoice_fiscal_imagen_tree").id,
                    'res_model': 'ct.invoice.fiscal.imagen',
                    'view_type': 'list',
                    'view_mode': 'list',
                    'context': {'edit': 1, 'create': 0, 'active_id': self.id},
                    'domain': domain,
            }
            return action
        else:
            raise UserError('No hay Documentos Fiscales!')

    def invoice_fiscal_ids(self):
        self.ensure_one()
        invoice=""
        for p in self.order_ids:
            for p in self.order_ids:
                if invoice:
                    invoice = invoice + p.invoice_ids
                else:
                    invoice = p.invoice_ids
        return invoice.ids

    #---- Muestra los Documentos Vinculados al Container
    def action_view_related_container_invoice_loads(self):
        self.ensure_one()
        invoice=""
        for p in self.order_ids:
             if invoice:
                 invoice=invoice + p.invoice_ids
             else:
                 invoice=p.invoice_ids
        if len(invoice)==0:
            raise UserError('No Existen documentos cargados...')
        invoice=invoice.filtered(lambda x: x.type=='out_invoice' and x.state=='posted')

        domain = [('id', 'in', invoice.ids)]
        action = {
            'name': _('Facturas Cargadas'),
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref("ct_logistic.view_ct_logistic_account_move_check_list_tree").id,
            'res_model': 'account.move',
            'view_type': 'list',
            'view_mode': 'list',
            'context': {'edit': 1,'create': 0, 'active_id': self.id},
            'domain': domain,
        }
        return action

    def get_invoice_fiscal(self):
        self.ensure_one()
        return self.env['ct.invoice.fiscal.imagen'].search([
                ('account_move_id', 'in', self.invoice_fiscal_ids() )
        ])

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------



"""
class ContainerLine(models.Model):
    _name="ct.logistic.container.line"
    _description="Lineas de Container"

    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container',
        ondelete='restrict',
        index=True)

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido',
        ondelete='restrict',
        required=True,
        domain=[('is_load','=',False),('status_invoice','=','invoiced')],
        index=True)

    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        related="sale_order_id.user_id",
        index=True)

    date_delivered=fields.Date('Fecha/Despacho')

    state_delivered=fields.Boolean('Despachado (S/N)', default=False)

    @api.onchange('date_delivered')
    def _onchange_date_delivered(self):
        if self.container_id.state!='transit':
            raise  UserError('No se puede marcar como despachado porque el Contenedor no esta en Transito!')
        if self.date_delivered:
           self.state_delivered=True
           #---- Actualizamos las Facturas
           for i in self.sale_order_id.invoice_ids.filtered(lambda x: x.state=='posted'):
               i.updateForSaleOrder(self.date_delivered)
        else:
          if self.sale_order_id:
              for i in self.sale_order_id.invoice_ids.filtered(lambda x: x.state == 'posted'):
                    self.state_delivered=False
                    i._unlink_ForSaleOrder()

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        if self.sale_order_id.is_load:
            raise UserError('Este Pedido ya esta cargado...')




    # ---- Campos Related
    property_partner_name = fields.Char('Cliente', related="sale_order_id.partner_id.display_name")
    # ---- Campos Related
    property_partner_locate = fields.Char('Localizacion', related="sale_order_id.partner_id.city")

    # ---- Campos Related Status Invoice
    #property_invoice_status = fields.Char('Estado/Facturacion', related="sale_order_id.invoice_status")

    # ---- Campos Related Packing o Bultos
    property_packing=fields.Integer("#Paquetes/Bultos", related="sale_order_id.packing_register")

    state = fields.Selection([
        ('draft', 'Pendiente'),
        ('partial', 'Parcial'),
        ('done', 'Despachado')
    ], string='Estado/Despacho', copy=False, index=True, default='draft', store=True, required=True)

"""







