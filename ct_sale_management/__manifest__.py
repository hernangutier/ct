# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modulo de Ventas Adaptado',
    'version' : '1.1',
    'summary': 'Modificacion al Modulo de Ventas, para agregar funcionalidad: Pedido por Departamentos, '
               'Actualizacion de cambio automatico en lista de precios, comfirmacion, facturacion inmediata, '
               'reservas y reportes sobre pedidos...',
    'sequence': 30,
    'description': """
        
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','sale','account','stock','ct_products','ct_res_partner_limit_credit','ct_res_partner', 'ct_commons_report', 'ct_account'],
    'data': [
        'views/wz_picking_post.xml',
        'views/wz_confirm.xml',
        'views/products_reserved_view.xml',
        'views/menu.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_view.xml',
        'views/template.xml',
        'report/report.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
