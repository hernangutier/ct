# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modulo para Realizar MIgracion de Data',
    'version' : '1.1',
    'summary': 'Migracion',
    'sequence': 30,
    'description': """
        Migrar: Productos, Clientes etc...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','ct_products'],
    'data': [
        'views/views.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
