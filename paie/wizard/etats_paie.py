# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class cnss_wizard(models.TransientModel):
    _name = "cnss.wizard"
    _description = "CNSS"

    @api.onchange('mois1','mois2','mois3')
    def onchange_date(self):
        debut = fin = None
        for record in self:
            if record.mois3:
               debut = record.mois3.date_start
            if record.mois2:
               debut = record.mois2.date_start
            if record.mois1:
               debut = record.mois1.date_start
            if record.mois1:
               fin = record.mois1.date_end
            if record.mois2:
               fin = record.mois2.date_end
            if record.mois3:
               fin = record.mois3.date_end
            record.debut = debut
            record.fin = fin
    mois1 = fields.Many2one('hr.payslip.run', 'Mois 1', required=True)
    mois2 = fields.Many2one('hr.payslip.run', 'Mois 2')
    mois3 = fields.Many2one('hr.payslip.run', 'Mois 3')
    debut = fields.Date("Debut")
    fin = fields.Date("Fin")

    def generate_report(self):
        if (not self.env.user.company_id.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.user.company_id.external_report_layout_id):
            raise UserError(_("You have to set your reports's header and footer layout."))
        data = {'mois1': self.mois1.id,'mois2': self.mois2.id,'mois3': self.mois3.id,'debut':self.debut,'fin':self.fin}
        return self.env.ref('paie.cnss_report').report_action([], data=data)