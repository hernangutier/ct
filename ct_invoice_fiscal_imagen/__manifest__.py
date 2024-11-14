# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Imagen de Facturacion Fiscal',
    'version': '1.1',
    'summary': 'Facturacion',
    'sequence': 30,
    'description': """
        Genera Registro de Facturacion Fiscal para Pedidos...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends': ['base', 'stock', 'sale_management', 'account'],
    'data': [
        'views/products.xml',
        'wizard/dialog_report.xml',
        'views/image_views.xml',
        'wizard/dialog_image_create.xml',
        'views/account_move.xml',
        'views/menu.xml',
        'security/ct_invoice_fiscal_imagen_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
