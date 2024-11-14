import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class WzContainerPost(models.TransientModel):
    _name="ct.logistic.container.post.form"
    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container',
        ondelete='restrict',
        required=True,
        index=True)
    date_finish=fields.Date('Fecha de Cierre')
    sale_order_close_date=fields.Boolean('Cerrar Documentos con fecha de Cierre?', default=True)


    def action_post_recode(self):
        #--- Chequear que todos los Pedido esten Facturados
        data = ""
        if self.container_id.date_init>self.date_finish:
            raise UserError('La Fecha de Cierre no puede ser menor a la Fecha de Salida!')
        if len(self.container_id.order_ids)<0:
            raise UserError('No hay Pedidos Cargados en el Container!')
        if self.sale_order_close_date:
           #--- Chacamos que todos los Pedidos Tengan Facturas
           for s in self.container_id.order_ids:
               if s.invoice_status!='invoiced':
                   raise UserError('Por Favor Revise el Pedido #: ' + s.name + 'no esta perparado para cerrar!')
               else:
                   if data == "":
                       data = s.invoice_ids
                   else:
                       data = data + s.invoice_ids
           #---- Procedemos a Cerrar las Facturas ---
           for f in data:
               f.write({
                   'date_delivered': self.date_finish,
                   'state_delivered': True,
                   'date_due_delivered': f.recalculate_due(self.date_finish)
               })
        self.close_order_ids()
        self.container_id.commit_with_date(self.date_finish)




    def close_order_ids(self):
        for s in self.container_id.order_ids:
            s.write({
                'state_delivered': True
            })

    def action_post(self):
        data=""
        if self.sale_order_close_date:
            for s in self.container_id.order_ids:
               if data=="":
                   data=s.sale_order_id.invoice_ids
               else:
                   data= data + s.sale_order_id.invoice_ids
            #----- Filtramos la Data
            data=data.filtered(lambda x: x.state=='posted' and x.state_delivered==False)
            for f in data:
                f.write({
                    'date_delivered': self.date_finish,
                    'state_delivered': True,
                    'date_due_delivered' : f.recalculate_due(self.date_finish)
                })
        obj=self.container_id.write({
            'state': 'done',
            'date_end': self.date_finish
        })
        return obj

#----------------------------------------------------
# Dialogo para Trasladar Pedidos de Container a
# Otro Container
#----------------------------------------------------
class dialogContainerTraslate(models.TransientModel):
    _name="ct.logistic.dialog.container.traslate"

    container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container de Origen',
        ondelete='restrict',
        require=True,
        index=True)

    finish_container_id = fields.Many2one(
        'ct.logistic.container',
        string='Container de Destino',
        ondelete='restrict',
        require=True,
        index=True)


    def post(self):
        #----- Restricciones
        if self.container_id==self.finish_container_id:
            raise UserError('Container de Origen y Destino son Iguales 1...')
        if self.container_id.state!='draft': raise UserError('El container de Origen no se encuetra en Carga... es Imposible Tranladar...')
        if self.finish_container_id.state != 'draft': raise UserError('El container de Origen no se encuetra en Carga... es Imposible Tranladar...')
        if len(self.container_id.order_ids.ids)==0:
            raise UserError("El container " + self.container_id.name + " no tiene pedidos a trasladar!")
        #---- Obtenemos los Vals a Eliminar y los que se van a Insertar
        self.finish_container_id.order_ids=self.container_id.order_ids.ids + self.finish_container_id.order_ids.ids
        self.container_id.order_ids = [(5, 0, 0)]
        for s in self.finish_container_id.order_ids:
            s.write({
                'load': True,
                'info_delivered': self.finish_container_id.name
            })



