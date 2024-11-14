import time
import math
import logging
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)



# --------------------------------------------------------------------
#
#   Modelo que recibe los Pedidos Moviles
#
# --------------------------------------------------------------------

# ----------------- SaleOrderMovile Master Class ---------------------
class SaleOrderMovile(models.Model):
    _name = "ct.sale.order.movile"
    # ---- Referencia de Pedido  -----
    name = fields.Char('Referencia', default='Nuevo')
    #------ Ordenes Generadas --------
    sale_order_generated=fields.Char('Ordenes Generadas')
    # ---- Tipo de Pedido -----
    require_fiscal= fields.Boolean('Solicita/Factura/Fiscal', default=False)
    # ---- Cliente --------
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        ondelete='restrict',
        index=True)
    #------ Status de el Pedido Movil ---
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('done', 'Procesado'),
        ('cancel', 'Cancelado'),
    ], string='Estado/Pedido', copy=False, index=True, default='draft', store=True, required=True)
    # ----= Asesor de Ventas ----
    user_id = fields.Many2one(
        'res.users',
        string='Asesor/Ventas',
        ondelete='restrict',
        index=True)
    #----- Notas Sobre el Pedido -----
    note = fields.Text('Notas')
    #-------- Lineas de Pedido -------
    order_lines = fields.One2many('ct.sale.order.movile.line', 'order_id', string='Order Lines',
                                  copy=True,
                                  auto_join=True)
    #--------- Count de las Lineas de Pedido ----
    order_line_count = fields.Integer('Total Lineas: ', compute="_compute_order_line_count")

    # ------------ Contador de Lineas de Pedido ----
    def _compute_order_line_count(self):
        for imagen in self:
            imagen.order_line_count = len(imagen.order_lines)

    # ---- Este Metodo crea los Presupuestos de Ventas por Departamentos de Ventas
    def action_confirm(self):
        #------- Variables Locales -----
        product_ids = []
        segment=[]
        orders=''
        # ---------- Obtenemos los Ids de los Productos ---
        for lines in self.order_lines:
            product_ids.append(
                lines.product_id.id
            )
        # ---- Agrupamos pos Departamento para Obtener los Ids de los Departamentos
        lines_grouped = self.env['product.product'].read_group(
            [('id', 'in', (product_ids))],
            ['name'],
            ['departament_id']
        )
        # ---  Creamos la Ordenes de Pedido Por Departamento  ---
        for gruop in lines_grouped:
            # ---  Preparamos las Lineas por Departamento ---
            departament_id=self.env['ct.product.departament'].browse(int(gruop['departament_id'][0]))

            new_line = []
            for l in self.order_lines.filtered(
                    lambda x: x.product_id.departament_id.id == int(gruop['departament_id'][0])):
                vals = (0, 0, {
                    'product_id': l.product_id.id,
                    'product_uom_qty': l.qty,
                    'product_uom': l.product_uom_id.id
                })
                new_line.append(vals)
                if len(new_line)==20:
                        #---- Crear un Pedido
                        sale = self.env['sale.order']
                        sale = sale.create({
                            'sale_order_movile_id': self.id,
                            'partner_id': self.partner_id.id,
                            'require_fiscal': self.require_fiscal,
                            'payment_term_id': departament_id.payment_term_id.id if departament_id.payment_term_id.id else self.partner_id.property_payment_term_id.id,
                            'departament_id': int(gruop['departament_id'][0]),
                            'order_line': new_line
                        })
                        orders += sale.name + ','
                        new_line=[]
            if len(new_line)>0:
                sale = self.env['sale.order']
                sale = sale.create({
                    'sale_order_movile_id': self.id,
                    'require_fiscal': self.require_fiscal,
                    'partner_id': self.partner_id.id,
                    'payment_term_id': departament_id.payment_term_id.id if departament_id.payment_term_id.id else self.partner_id.property_payment_term_id.id,
                    'departament_id': int(gruop['departament_id'][0]),
                    'order_line': new_line
                })
                orders += sale.name + ','
        #----- Actualizamos el Estatus de el Pedido ----
        self.write({
            'state': 'done',
            'sale_order_generated': orders[:len(orders)-1]
        })
        return self

    def action_cancel(self):
        self.state.write({
            'state': 'cancel'
        })
        return self

    # ----- Modificamos el Metodo Crear para Generar la Secuencia
    @api.model
    def create(self, vals):
        # self._check_lines_retrict(vals)
        if "name" not in vals or vals["name"] == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code('npm')
        saleordermovile = super(SaleOrderMovile, self).create(vals)
        return saleordermovile
    #------ Anulamos la Eliminacion de este Registro ---
    def unlink(self):
        raise UserError('No esta permitido eliminar este Registro!')


# -------------- SaleOrderMovileLine Detail Class ---------------------
class SaleOrderMovileLine(models.Model):
    _name = "ct.sale.order.movile.line"
    order_id = fields.Many2one('hgl.sale.order.movile', string='Ref. Orden', required=True, ondelete='cascade',
                               index=True,
                               copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        ondelete='restrict',
        index=True)

    qty = fields.Float('Cantidad')

    @api.constrains('product_uom_id')
    def _check_product_uom_id(self):
        if self.product_uom_id != self.product_id.uom_id and self.product_uom_id != self.product_id.uom_po_id:
            raise UserError('Unidad de Medida Erronea en ' + self.product_id.name)

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Udm',
        ondelete='restrict',
        index=True)
    #---- Para Mostrar el Departamento de Fcaruracion ----
    departament_name = fields.Char('Dep./Facturacion', related="product_id.departament_id.name", readolny=True)
