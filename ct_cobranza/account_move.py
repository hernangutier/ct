import time
import math
from datetime import date
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models,_

class AccountMove(models.Model):
    _inherit="account.move"
    #---- Estatus para Marcar Despacho
    state_delivered=fields.Boolean('Despachado (S/N)',  store=True)
    # ---- Fecha Exacta de el Despacho
    date_delivered=fields.Date('Fecha/Despacho', store=True)
    # ---- Fecha Estimada de el Vencimiento de la Factura
    date_due_delivered=fields.Date('Fecha/Vencimiento c/Despacho', store=True)

    def updateForSaleOrder(self, date):
        self.write({
            'date_delivered': date,
            'date_due_delivered': self.recalculate_due(date),
            'state_delivered': True
        })

    def _unlink_ForSaleOrder(self):
        self.write({
            'date_delivered': None,
            'date_due_delivered': None,
            'state_delivered': False
        })

    def recalculate_due(self, date):
        date_end=datetime.datetime.strptime(str(date), "%Y-%m-%d")
        return date_end + datetime.timedelta(days=int((self.invoice_date_due - self.invoice_date).days))

    def recalculate_due_for_int_days(self, date, v_days):
        date_end = datetime.datetime.strptime(str(date), "%Y-%m-%d")
        return date_end + datetime.timedelta(v_days)

    def updateToContainer(self):
        active_id = self._context.get('active_id')
        container = self.env['ct.logistic.container'].browse(int(active_id))
        if container:
            if container.state!='transit':
                raise UserError('Container no esta en transito...')
            else:
                self.write({
                    'date_due_delivered': i.recalculate_due(self.date_delivered),
                    'state_delivered': True
                })
                #---- Pendiente Actualizar el Pedido

    """
    def _check_is_container(self):
        line = []
        sale_order = self.env['sale.order'].search([('name', '=', str(self.invoice_origin))], limit=1)
        if sale_order:
            container = self.env['ct.logistic.container'].search([('name', '=', str(sale_order.info_delivered))])
            if container:
                if container.type=='glp':
                        #--- Poedmos actualizar
                        self.write({
                            'date_due_delivered': self.recalculate_due(self.date_delivered),
                            'state_delivered': True
                        })
                        raise UserError('Debe marcar la factura desde el Container: ' + container.name)
                else:
                        raise UserError('Debe marcar la factura desde el Container: ' + container.name )
            else:
                #--- No hay Container Asignado
                container=self.env['ct.logistic.container'].search([])
                vals = (0, 0, {
                    'sale_order_id': sale_order.id,
                    'state': 'done'
                })
                line.append(vals)
                container = self.env['ct.logistic.container'].search([])
                container.create({
                    'type': 'glp',
                    'date_init': self.date_delivered,
                    'date_end': self.date_delivered,
                    'container_line_ids': line,
                    'state': 'done'
                })
                # ---- Actualizamos la Fecha de Vencimiento
                self.write({
                    'date_due_delivered': self.recalculate_due(self.date_delivered),
                    'state_delivered': True
                })
    """

    #---- Eventos de Cambio ----
    @api.onchange('date_delivered')
    def _onchange_date_delivered(self):
        if self.date_delivered:
            #--- Leemos la Orden de Ventas ---
            sale_order = self.env['sale.order'].search([
                ('name', '=', self.invoice_origin)
            ], limit=1)
            if sale_order:
                #---- Determinamos si esta en Guia --
                container=self.env['ct.logistic.container'].search([('name','=',sale_order.name)])
                if container:
                    if container.state=='transit':
                        self.write({
                            'date_due_delivered': self.recalculate_due(self.date_delivered),
                            'state_delivered': True
                        })
                        sale_order.write({
                            'state_delivered': True,
                        })
                    else:
                        raise UserError('El container debe estar en transito para cerrar Facturas...')
                else:
                    self.write({
                        'date_due_delivered': self.recalculate_due(self.date_delivered),
                        'state_delivered': True
                    })
                    #---- Actualizar el Pedido ---#
                    sale_order.write({
                        'state_delivered': True,
                        'info_delivered' : "Despachado en la Empresa"
                    })
            else:
                self.write({
                    'date_due_delivered': self.recalculate_due(self.date_delivered),
                    'state_delivered': True
                })
        else:
            self.write({
                'date_due_delivered': None,
                'state_delivered': False
            })

    # ---- Eventos de Cambio ----
    @api.onchange('invoice_payment_term_id')
    def _onchange_payment_term(self):
        for line in self.invoice_payment_term_id.line_ids:
            if line:
                break
        if self.date_delivered:
            self.write({
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_date_due': self.recalculate_due_for_int_days(self.date_delivered, line.days)
            })
        else:
            self.write({
                'invoice_payment_term_id': self.payment_term_id.id,
                'invoice_date_due': self.recalculate_due_for_int_days(self.invoice_date, line.days)
            })


















