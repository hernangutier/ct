import time
import math
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#--------------------------------------------------------------------
#
# Campos adicionales de forma para product.template
#
#--------------------------------------------------------------------

# ------ Modelos Auxiliares -----------------
class ProductBrands(models.Model):
        _name = "ct.product.brands"
        _description = "Marcas"
        name = fields.Char('Denominacion', copy=True, store=True, required=True)

        product_count = fields.Integer('count', compute="_compute_product_count")

        def _compute_product_count(self):
            self.product_count = len(self.env['product.template'].search([('brand_id', '=', self.id)]))

class ProductsDepartament(models.Model):
        _name = "ct.product.departament"
        _description="Departamentos"
        code = fields.Char('Codigo', required=True)
        name = fields.Char("Denominacion", copy=True, required=True)
        descripcion = fields.Text('Descripcion de el Departamento')
        confirm_invoice_inmediate=fields.Boolean('Permite Trasferencia y Facturacion Inmediata', default=False)
        product_count=fields.Integer('count',compute="_compute_product_count")
        #----- Campo para desactivar el Control Estricto por Departamento
        restrict_control_homogen=fields.Boolean('Sin/Control Departamental', default=False)

        #--- Plazos de Pago por Defecto para esta Facturacion
        payment_term_id = fields.Many2one(
            'account.payment.term',
            string='Terminos de Pago para esta Facturacion',
            ondelete='restrict',
            index=True)
        def _compute_product_count(self):
            self.product_count=len(self.env['product.template'].search([('departament_id','=',self.id)]))
        # ---------- Constrains --------
        _sql_constraints = [
            ('code_unique', 'UNIQUE(code)', 'Este codigo ya esta en Uso!'),
        ]

        def name_get(self):
            result = []
            for p in self:
                name = '(%s) %s' % (p.code, p.name)
                result.append((p.id, name))
            return result

class ProductsLocations(models.Model):
    _name="ct.product.locations"
    _description = "Localizacion"
    code=fields.Char('Codigo', required=True)
    name=fields.Char('Denominacion', required=True)


class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    old_sku=fields.Char('Sku Anterior')

    #------ Nuevos Campos al Modelo ----
    emin=fields.Integer('Min. Venta', default=1)
    qty_packing=fields.Integer('Cnt. Presentacion', default=1)
    #----- Campo establecido para imprimir como consolidable ---
    is_consolidable=fields.Boolean('Es Consolidable', default=False)
    #-----------------------------------------------------------
    #-----------------------------------
    type_origim = fields.Selection([
        ('nac', 'Nacional'),
        ('import', 'Importado'),
    ], string='Tipo Producto Origen', copy=False, index=True, default='nac', store=True, required=True)
    sku_prov = fields.Char('Sku Proveedor', copy=False, store=True, required=False)
    # ---- Marca o Fabricante --------
    brand_id = fields.Many2one(
        'ct.product.brands',
        string='Marca o Fabricante',
        ondelete='restrict',
        index=True)
    # ----- Departamento para Facturacion ---
    departament_id = fields.Many2one(
        'ct.product.departament',
        string='Departamento de Facturacion',
        ondelete='restrict',
        required=True,
        index=True)
    # ----- Localizacion Fisica ---
    location_fisical_id = fields.Many2one(
        'ct.product.locations',
        string='Ubicacion Fisica',
        ondelete='restrict',
        required=True,
        index=True)
    # ------ Cantidad Factiurada no Despachada ---
    qty_invoice_not_delivered = fields.Integer('Qty. No Despachada', compute="get_qty_not_delivered")

    def get_qty_not_delivered(self):

        for p in self:
            sum = 0
            lines = self.env['account.move.line'].sudo().search([('product_id', '=', p.product_variant_id.id)]).filtered(
                lambda
                    x: x.move_id.type == 'out_invoice' and x.move_id.state_delivered == False and x.move_id.state == 'posted'
            )
            for l in lines:
                sum = sum + l.quantity
            p.qty_invoice_not_delivered = sum


class ProductPriceList(models.Model):
    _inherit="product.pricelist"

    def action_get_partner(self):

        self.ensure_one()
        c=self.env['res.partner'].search([]).filtered(lambda x: x.property_product_pricelist.id == self.id)
        domain = [('id', 'in', c.ids)]
        action = {
            'name': _('Clientes'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'context': {'edit': 1, 'create': 0},
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action
