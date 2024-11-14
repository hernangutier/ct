# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Control Logistico de Pedidos',
    'version' : '1.1',
    'summary': 'lOGISTICA',
    'sequence': 30,
    'description': """
        Guias de despacho, despachos por almacen, despachos por encomiendas etc...
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','sale_management','account','ct_res_partner_limit_credit', 'ct_sale_management','fleet','ct_invoice_fiscal_imagen', 'ct_commons_report'],
    'data': [
        'security/ct_logistic_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/sale_order_wait_views.xml',
        'views/account_move_check_list.xml',
        'wizard/wz_update_container.xml',
        'wizard/wz_container_post.xml',
        'wizard/container_summary_form.xml',
        'views/menu.xml',
        'views/container_views.xml',
        'views/container_views.xml',
        'views/report_views.xml',
        'views/sale_order_form.xml',
        'report/report.xml',
        'report/body.xml',
        'report/template.xml',
        'data/data.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
