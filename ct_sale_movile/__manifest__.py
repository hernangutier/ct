# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Pedidos Moviles App',
    'version' : '1.1',
    'summary': 'Sales',
    'sequence': 30,
    'description': """
        Este modulo crea los modelos para las imagenes de pedidos moviles
        trasferidas desde Apps...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','account','sale','ct_commons_report'],
    'data': [
        'views/menu.xml',
        'views/views.xml',
        'views/template.xml',
        'views/report.xml',
        'wizard/wizard_report.xml',
        'security/ir.model.access.csv',
        'data/data.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
