# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modificacion al Modulo de Pagos',
    'version' : '1.1',
    'summary': 'Numero de Control y otros campos de Control',
    'sequence': 30,
    'description': """
        Pagos
        
    """,
    'category': 'Sales',
    'depends' : ['base','account','ct_commons_report'],
    'data': [
        'wizard/wz_views.xml',
        'data/data.xml',
        'views/account_payment.xml',
        'views/template.xml',
        'views/menu.xml',

        'wizard/report.xml',
    ],
    'demo': [
        #'demo/account_demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
