# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Autogenerar Codigo Comercial',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Crea una secuencia cc para Autogenerar los Codigos comerciales de Clientes...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','sale'],
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
