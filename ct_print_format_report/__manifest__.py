# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Reportes PDF en Formatos Media Carta, Carta, Oficio',
    'version': '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Reportes en PDF en Diversidad de Formatos 
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends': ['base', 'sale', 'ct_commons_report', 'account','stock'],
    'data': [

        'report/headers.xml',
        'report/footers.xml',
        'report/bodys.xml',
        'report/seccions.xml',
        'report/template.xml',
        'report/report.xml'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
