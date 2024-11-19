from odoo import fields, models, api

#--------------------------------------------------------------------
#
# Contenedor de Categorias para Listas de Precios Configuradas
#
#--------------------------------------------------------------------
class ContainerCategory(models.Model):
    _name = 'ct.list.price.container.category'
    _description = 'Contenedor de Categorias'
    #--- Nombre de la Lista
    name = fields.Char('Denominacion', required=True)
    #---- Categorias Hijas a Mostrar
    categ_childs_ids = fields.Many2many(
        'product.category', string='Categorias Hijas')
