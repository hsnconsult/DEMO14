# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from functools import partial
from odoo.osv import expression

import psycopg2
import pytz
import locale

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp


class ReportCNSS(models.AbstractModel):

    _name = 'report.paie.report_cnss'

    def _etat_cnss(self,mois1,mois2,mois3):
        if mois1 == False:
           mois1=0
        if mois2 == False:
           mois2=0
        if mois3 == False:
           mois3=0 
        cr = self.env.cr
        requete = "WITH mois1 AS " \
                  "(SELECT p.employee_id as emp_id, l.amount as basecnss, l.amount*21.5/100 as cnss " \
                  "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                  "WHERE l.slip_id = p.id " \
                  "AND p.payslip_run_id = r.id " \
                  "AND l.code = 'BCNSS' " \
                  "AND r.id ="+str(mois1)+"), " \
                  "mois2 AS " \
                  "(SELECT p.employee_id as emp_id, l.amount as basecnss, l.amount*21.5/100 as cnss " \
                  "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                  "WHERE l.slip_id = p.id " \
                  "AND p.payslip_run_id = r.id " \
                  "AND l.code = 'BCNSS' " \
                  "AND r.id ="+str(mois2)+"), " \
                  "mois3 AS " \
                  "(SELECT p.employee_id as emp_id, l.amount as basecnss, l.amount*21.5/100 as cnss " \
                  "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                  "WHERE l.slip_id = p.id " \
                  "AND p.payslip_run_id = r.id " \
                  "AND l.code = 'BCNSS' " \
                  "AND r.id ="+str(mois3)+") " \
                  "SELECT e.ordre, e.name as nom, j.name as profession, e.secsoc, coalesce(mois1.basecnss,0)+coalesce(mois2.basecnss,0)+coalesce(mois3.basecnss,0) as basecnss, coalesce(mois1.cnss,0) as cnss1, coalesce(mois2.cnss,0) as cnss2, coalesce(mois3.cnss,0) as cnss3, c.date_start " \
                  "FROM hr_employee e " \
                  "LEFT JOIN hr_contract c " \
                  "ON c.employee_id = e.id " \
                  "LEFT JOIN hr_job j " \
                  "ON e.job_id = j.id " \
                  "LEFT JOIN mois1 " \
                  "ON mois1.emp_id = e.id " \
                  "LEFT JOIN mois2 " \
                  "ON mois2.emp_id = e.id " \
                  "LEFT JOIN mois3 " \
                  "ON mois3.emp_id = e.id " \
                  "WHERE e.active is True " \
                  "ORDER BY e.ordre " \
        #raise UserError(requete)
        cr.execute(requete)
        alines = cr.dictfetchall()
        return {
            'alines': alines,
            }

    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self._etat_cnss(data['mois1'],data['mois2'],data['mois3']))
        #locale.setlocale(locale.LC_ALL, 'fr_FR')
        return data