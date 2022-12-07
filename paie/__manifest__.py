# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'paie',
    'version' : '1.1',
    'summary': 'Permet de gérer la paie',
    'sequence': 180,
    'description': """
Gestion de la paie
====================
    """,
    'category': 'Ressources humaines',
    'website': 'http://www.hsnconsult.com',
    'depends': ['hr','hr_contract','hr_payroll','report_xlsx'],
    'data': [
        'views/paie_view.xml',
        'views/pret_view.xml',
        'views/paie_report.xml',
        'wizard/paie_report.xml',
        'wizard/report_cnss.xml',
        'views/report_bulletin.xml',
        'views/report_salarie.xml',
        'views/report_ordre.xml',
        'views/report_iuts.xml',
        'views/report_virement.xml',
        'views/report_billetage.xml',
        'views/report_cheque.xml',
        'views/report_livrep.xml',
        'views/report_cnss.xml',
        'wizard/etats_paie.xml',
        'security/paie_security.xml',
        'security/ir.model.access.csv',
                ],
    'installable': True,
    'application': True,
    'auto_install': False
}
