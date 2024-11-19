# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Generar Listas de Precios',
    'version' : '1.1',
    'summary': 'Ventas',
    'sequence': 30,
    'description': """
        Generador de Listas de Precios....
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base', 'product','ct_products','sale_management','sale'],
    'data': [
        'report/report.xml',
        'wizard/dialog.xml',
        'views/container_category.xml',
        'views/menu.xml',
        'views/new_product_card.xml',
        'views/template.xml',
        'views/company_view.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
