# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modulo para Control de Cobranza (Contra Despacho)',
    'version' : '1.1',
    'summary': 'Cobranza ',
    'sequence': 30,
    'description': """
        Consulta de Cuentas por Cobrar sobre despacho, Control de Efetivo...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','sale_management','account','ct_payment','ct_res_partner_limit_credit', 'ct_sale_management','fleet','ct_logistic', 'ct_commons_report'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'wizard/wz_cobranza_form.xml',
        'views/menu.xml',
        'report/body.xml',
        'report/report.xml',


    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
