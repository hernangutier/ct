# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Caracteristicas Adicionales en la Contabilidad Basica',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Caracteristicas y Funciones adicionales en la Facturacion y Contabilidad
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','account'],
    'data': [
        'views/views.xml',
        'views/menu.xml',
        'data/data.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
