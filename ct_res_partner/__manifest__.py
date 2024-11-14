# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Localizacion Clientes y Proveedores',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Localidades, Estados etc...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','sale','ct_commons_report','account'],
    'data': [
        'views/res_partner_views.xml',
        'wizard/report_wz.xml',
        'views/menu.xml',
        'data/data.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
