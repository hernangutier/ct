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
        'wizard/wizards.xml',
        'views/container_category.xml',
        'views/menu.xml',
        'report/product_card.xml',
        'report/template.xml',
        'views/company_view.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
