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
    'depends' : ['base','stock'],
    'data': [
        'security/ir.model.access.csv',
        #'views/menu.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
