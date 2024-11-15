# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Auditorias de Inventario',
    'version': '1.1',
    'summary': 'Auditorias',
    'sequence': 30,
    'description': """
        Vista y control de auditorias casos de inventario...


    """,
    'category': 'HGL-ADECUACION',
    'depends': ['base', 'stock'],
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/menu.xml',


    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
