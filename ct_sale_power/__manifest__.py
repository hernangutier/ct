# Copyright 2020, HGL Sistemas, FP.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Fuerza de Ventas',
    'summary': 'Este Modulo permite calcular comisiones sobre facturas de Ventas totalmente pagadas'
               ' asi como generar soportes de pago a los asesores de ventas, penalizaciones, y demas operacions'
               '',
    'version': '13.0.1.0.0',
    'category': 'Reports',
    'author': 'Hernan Gutierrez,'
              'HGL SISTEMAS FP.',
    'website': "https://hglsistemas.com",
    'license': 'LGPL-3',
    'depends': [
        'base','stock','account','ct_products', 'ct_logistic', 'ct_cobranza','ct_commons_report',
    ],
    'data': [
        'wizard/wizard.xml',
        'data/data.xml',
        'views/product_views.xml',
        'views/menu.xml',
        'views/commissions.xml',
        'views/account.xml',
        'report/template.xml',
        'report/report.xml',
        'security/ct_sale_power_security.xml',
        'security/ir.model.access.csv',


        #'wizard/wizard.xml',
    ],
    'qweb': [
        'static/src/xml/button.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
