import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Campos adicionales de forma para Clientes y Proveedores
#
#--------------------------------------------------------------------

class Locations(models.Model):
    _name="ct.partner.locations"
    _description = "Localidades"
    name=fields.Char('Denominacion',required=True)
    # ----- Departamento para Facturacion ---
    state_id = fields.Many2one(
        'res.country.state',
        string='Estado',
        ondelete='restrict',
        required=True,
        index=True)


class ResPartner(models.Model):
    _inherit="res.partner"
    #--------- Campos Reconfigurados  --------------------------
    street = fields.Text('Direccion', required=True)
    city = fields.Char('Ciudad o Pueblo', required=True)
    vat = fields.Char('Rif.', required=True)
    ref = fields.Char('Código de Comercial', help="Codigo Comercial...")
    locations_id = fields.Many2one(
        'ct.partner.locations',
        string='Estado',
        ondelete='restrict',
        required=True,
        index=True)
    #-----------------------------------------------------------
    # -------- Saldos de el Cliente -----------
    customer_due_amount = fields.Float('Saldo (Cliente)', compute="get_due_customer")
    # -----------------------------------------
    # -------- Saldos de el Proveedor -----------
    supplier_due_amount = fields.Float('Saldo (Proveedor)', compute="get_due_supplier")

    # ------- Campo para Manejo de Sucursales -----
    is_sucursal = fields.Boolean('Es Sucursal', default=False)

    def name_get(self):
        result=[]
        for p in self:
            name='(%s) %s' % (p.vat,p.name)
            result.append((p.id, name))
        return result
    #-------------------- Saldo como Cliente ---------------
    def get_due_customer(self):
        date = fields.Date.today()
        for k in self:
            total = 0
            obj = self.env['account.move.line'].search([('partner_id', '=', k.id)])
            for i in obj:
                if i.move_id.state == "posted":
                    if i.account_id.internal_type in ['receivable','liquid']:
                        total = total + i.balance
            k.customer_due_amount = total
    #-------------------- Saldo como proveedor -------------
    def get_due_supplier(self):
        date = fields.Date.today()
        for k in self:
            total = 0
            obj = self.env['account.move.line'].search([('partner_id', '=', k.id)])
            for i in obj:
                if i.move_id.state == "posted":
                    #if i.reconciled == False and i.balance != 0:
                        #if i.account_id.reconcile == True:
                            if i.account_id.internal_type in ['payable']:
                                # print("i.name",i.balance)
                                total = total + i.balance
            k.supplier_due_amount = total

    

