# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Plantillas y Fuentes para Reportes PDF',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        static/src/fonts y template
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','sale','product'],
    'data': [
        'views/template.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
