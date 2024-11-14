# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Actualizacion Modelo Productos',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Marcas, Localizacion , Departamento de Facturacion etc...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','account'],
    'data': [
        'views/menu.xml',
        'views/product_views.xml',
        #'data/data.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
