# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Limite de Credito',
    'version' : '1.1',
    'summary': 'Account',
    'sequence': 30,
    'description': """
        Control de credito en pedidos (credito rotativo)
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','sale_management'],
    'data': [
        'views/res_partner_views.xml',
        #'wizard/kardex_wz.xml',
        #'views/template.xml',
        #'views/kardex_views.xml',
        #'views/menu.xml',
        #'views/product_template_views.xml',
        #'security/ir.model.access.csv'
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
