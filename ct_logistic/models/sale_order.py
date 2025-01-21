import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#-------------------------------------------------------------
#
#   Info. para control logistico Precargada  proveniente en
#   primera instancia de el Cliente
#-------------------------------------------------------------


class SaleOrder(models.Model):
    _inherit="sale.order"
    #------ Variable para Controlar estatus de Despacho ---
    state_delivered=fields.Boolean('Despachado (S/N)',  store=True)
    #---- Metodo para Indicar si el Pedido esta Cargado
    load=fields.Boolean('Cargado (S/N',default=False)
    # --------- Metodo Sugerido  --------
    delivery_proposal = fields.Selection([
        ('ddt', 'DDT'),
        ('glp', 'en Empresa'),
        ('enc', 'Encomienda')
    ], string='Sugerencia de Envio', copy=False, index=True, default='ddt', store=True, required=True)
    #--- Inforamcion de el Container ----
    info_delivered=fields.Text('Info. Container')

    #----------- Valores para Control de Gastos de Recuperacion ----
    recovery_expenses = fields.Float('% Gastos de Recuperacion', default=0.0)
    #---------------------------------------------------------------

    #-------- Agregamos Informacion de Utilidada para Agrupar pedidos ---


    #------ Onchange Partner Actualizamos los Valores de Despacho -----
    @api.onchange('partner_id')
    def _onchange_partner(self):
        super(SaleOrder, self)._onchange_partner()
        if self.partner_id.delivery_proposal:
            self.delivery_proposal=self.partner_id.delivery_proposal
            self.recovery_expenses=self.partner_id.recovery_expenses


    def close_dispatch_to_date(self):
        for f in self.invoice_ids:
            f.updateForSaleOrder(f.invoice_date)
        self.state_delivered=True
        return self

    def action_invoice_commit(self):
        to_invoce=0
        for r in self.order_line:
            if r.qty_delivered-r.qty_invoiced>0:
                to_invoce+=1
        if to_invoce==0 :
            raise UserError('No hay lineas a Facturar...')
        raise UserError('Facturar')


#------ Modelo para Establecer Ruta de Despacho Planificado -----
class Routes(models.Model):
        _name="ct.logistic.routes"
        name=fields.Char('Denominacion', required=True)
        ref=fields.Char("Ref.", required=True)
        #---- Estado ----
        res_country_state_id = fields.Many2one(
            'res.country.state',
            string='Estado',
            ondelete='restrict',
            index=True)
        #---- Ciudades --
        partnert_locations_ids = fields.Many2many(
            'ct.partner.locations',
            #domain=[('state_id', '=',  lambda self: self.res_country_state_id.id)],
            string='Ciudad/Localidad')

