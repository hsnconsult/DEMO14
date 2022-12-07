# -*- coding: utf-8 -*-
{
    'name': "etatper",

    'summary': """Etats personnalises""",

    'description': """
        Permet d'imprimer des etats personnalises
    """,

    'author': "HSN consult",
    'website': "http://www.hsnconsult.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

    # always loaded
    'data': [
        'views/report_views.xml',
        'views/report_proforma.xml',
        'views/report_proformaeng.xml',
        'views/report_facture.xml',
        'views/report_invoice.xml',
        'views/report_BL.xml', 
        'views/report_avanceimp.xml',
        'views/etatper_views.xml',
            ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
