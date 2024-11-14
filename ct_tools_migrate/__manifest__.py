# Copyright 2020, HGL Sistemas, FP.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Modulo para Migrar Datos al Sistema',
    'summary': 'Generate Kardex Report',
    'version': '13.0.1.0.0',
    'category': 'Reports',
    'author': 'Hernan Gutierrez,'
              'HGL SISTEMAS FP.',
    'website': "https://hglsistemas.com",
    'license': 'LGPL-3',
    'depends': [
        'stock','account'
    ],
    'data': [
        'views/views.xml',
        'views/template.xml',
        'wizard/wizard.xml',
    ],
    'qweb': [
        'static/src/xml/button.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
