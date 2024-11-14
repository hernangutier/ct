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
    'depends' : ['base'],
    'data': [
        'views/res_partner_views.xml',
        'data/data.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
