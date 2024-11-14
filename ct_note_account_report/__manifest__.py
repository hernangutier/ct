# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Imprimir Notas de Entregas y Facturas',
    'version' : '1.1',
    'summary': 'lOGISTICA',
    'sequence': 30,
    'description': """
        Imprimir Facturas, Notas de entrega, Picking con Formatos Medi Pagina
        
        
    """,
    'category': 'HGL-ADECUACION',
    'depends' : ['base','stock','sale_management','account'],
    'data': [
        #'views/account_move.xml',
        'report/header_footer.xml',
        'report/seccions.xml',
        'report/note_report_template.xml',
        'report/report.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
