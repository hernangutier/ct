from odoo import fields, models, api


class ContainerCategory(models.Model):
    _name = 'ct.list.price.container.category'
    _description = 'Contenedor de Categorias'
    name = fields.Char('Denominacion', required=True)
    categ_childs_ids = fields.Many2many(
        'product.category', string='Categorias Hijas')
