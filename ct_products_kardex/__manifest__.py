# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Kardex de Inventario',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Kardex Vista y Reporte Kardex PDF
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','ct_commons_report'],
    'data': [
        'views/report.xml',
        'wizard/kardex_wz.xml',
        'views/template.xml',
        'views/kardex_views.xml',
        'views/menu.xml',
        'views/product_template_views.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
