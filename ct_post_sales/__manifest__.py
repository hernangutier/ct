# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modulo de Post-Ventas (Garantias y Servicio Tecnico)',
    'version' : '1.1',
    'summary': 'Garantias y servicio tecnico',
    'sequence': 30,
    'description': """
        Pagos
    """,
    'category': 'Sales',
    'depends' : ['base','product','purchase_stock', 'sale_stock', 'stock', 'stock_account', 'account','ct_commons_report','ct_res_partner'],
    'data': [
        'security/ct_post_sales_security.xml',
        'security/ir.model.access.csv',
        'report/headers.xml',
        'report/bodys.xml',
        'report/template.xml',
        'report/report.xml',
        'data/data.xml',
        'views/views.xml',
        'views/menu.xml',

    ],
    'demo': [
        #'demo/account_demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
