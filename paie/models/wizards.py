# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from operator import ne
from threading import Condition
from odoo import models, fields, api, _
import re
from odoo.exceptions import UserError, ValidationError
#les differents transient classes

class PaieLivrePaiexlsx(models.AbstractModel):
    _name = "report.paie.report_livrepaiexlsx"
    _inherit="report.report_xlsx.abstract"
    _description = "Livre de paie excel"
    
    def _get_report_values(self, docids, data=None):
        return{
            "docids":docids,
            "lui":docids.ids,
        }
    def generate_xlsx_report(self, workbook, data, docids):
        
        lines=self._get_report_values(docids)
        selected_records=self.env['hr.payslip.run'].browse(lines['lui'])
        force=[]
        for record in selected_records:
            val={
                "id":record.id,
                "nom":record.name,
                "debut":record.date_start,
                "fin":record.date_end,
                "slip_ids":record.slip_ids,
            }
            force.append(val)
        bolth = workbook.add_format({'bold': 1,'align': 'center','fg_color': 'green','border': 1})
        boltd = workbook.add_format({'border': 1})
        my_format=workbook.add_format({'border': 1,'num_format':'dd/mm/yyyy'})
        boltdsep = workbook.add_format({'border': 1,'num_format':'# ##0'})
        ident = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'yellow'})
        identbo = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'orange'})
        for lot in force:
            worksheet = workbook.add_worksheet(lot['nom'])
            worksheet.set_column(0, 4, 15)
            col=0
            row=1
            worksheet.merge_range(0, col,0,col+4, lot['nom'],identbo)
            worksheet.write(row, col, 'Matricule',bolth)
            worksheet.write(row, col + 1, 'Nom Prénoms',bolth)
            worksheet.write(row, col + 2, 'Charges',bolth)
            worksheet.write(row, col+3, 'Date de début de contrat',bolth)
            worksheet.write(row, col + 4, 'Emploi occupé',bolth)
            worksheet.write(row, col + 5, 'Catégorie',bolth)
            worksheet.write(row, col + 6, 'Salaire de base',bolth)
            worksheet.write(row, col + 7, 'Prime ancienneté',bolth)
            worksheet.write(row, col + 8, 'Sursalaire',bolth)
            worksheet.write(row, col + 9, 'Indem Log',bolth)
            worksheet.write(row, col + 10, 'Indem Transp',bolth)
            worksheet.write(row, col + 11, 'Indem Resp',bolth)
            worksheet.write(row, col + 12, 'Indem Special',bolth)
            worksheet.write(row, col + 13, 'BRUT',bolth)
            worksheet.write(row, col + 14, 'CNSS 5.5%',bolth)
            worksheet.write(row, col + 15, 'CNSS 16%',bolth)
            worksheet.write(row, col + 16, 'TPA',bolth)
            worksheet.write(row, col + 17, 'IUTS',bolth)
            worksheet.write(row, col + 18, 'Pret/Avance',bolth)
            worksheet.write(row, col + 19, 'Mutuelle',bolth)
            worksheet.write(row, col + 20, 'Net à Payer',bolth)
            
            for bul in lot['slip_ids'].sorted(key=lambda line: line.employee_id.ordre):
                row+=1
                worksheet.write(row, col, bul.employee_id.identification_id,boltd)
                worksheet.write(row, col+1, bul.employee_id.name,boltd)
                worksheet.write(row, col+2, bul.employee_id.children,boltd)
                worksheet.write(row, col+3, bul.contract_id.date_start,my_format)
                worksheet.write(row, col+4, bul.employee_id.job_id.name,boltd)
                worksheet.write(row, col+5, bul.contract_id.idcategorie.name,boltd)
                worksheet.write(row, col+6, bul.sbasep,boltdsep)
                worksheet.write(row, col+7, bul.ancp,boltdsep)
                worksheet.write(row, col+8, bul.sursalp,boltdsep)
                worksheet.write(row, col+9, bul.logementp,boltdsep)
                worksheet.write(row, col+10, bul.transportp,boltdsep)
                worksheet.write(row, col+11, bul.fonctionp,boltdsep)
                worksheet.write(row, col+12, bul.indforp,boltdsep)
                worksheet.write(row, col+13, bul.brutp,boltdsep)
                worksheet.write(row, col+14, bul.chargesalp,boltdsep)
                worksheet.write(row, col+15, bul.chargepatp,boltdsep)
                worksheet.write(row, col+16, bul.tpa,boltdsep)
                worksheet.write(row, col+17, bul.iutsp,boltdsep)
                worksheet.write(row, col+18, bul.pretp,boltdsep)
                worksheet.write(row, col+19, bul.mutp,boltdsep)
                worksheet.write(row, col+20, bul.salnetp,boltdsep)

class PaieVirementxlsx(models.AbstractModel):
    _name = "report.paie.report_virementxlsx"
    _inherit="report.report_xlsx.abstract"
    _description = "Virement excel"
    
    def _get_report_values(self, docids, data=None):
        return{
            "docids":docids,
            "lui":docids.ids,
        }
    def generate_xlsx_report(self, workbook, data, docids):
        
        lines=self._get_report_values(docids)
        selected_records=self.env['hr.payslip.run'].browse(lines['lui'])
        force=[]
        for record in selected_records:
            val={
                "id":record.id,
                "nom":record.name,
                "debut":record.date_start,
                "fin":record.date_end,
                "slip_ids":record.slip_ids,
            }
            force.append(val)
        bolth = workbook.add_format({'bold': 1,'align': 'center','fg_color': 'blue','border': 1, 'color':'white'})
        boltd = workbook.add_format({'border': 1})
        my_format=workbook.add_format({'border': 1,'num_format':'dd/mm/yyyy'})
        boltdsep = workbook.add_format({'border': 1,'num_format':'# ##0'})
        ident = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'yellow'})
        identbo = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'orange'})
        for lot in force:
            worksheet = workbook.add_worksheet(lot['nom'])
            worksheet.set_column(0, 4, 15)
            col=0
            row=1
            worksheet.merge_range(0, col,0,col+7, lot['nom'],identbo)
            worksheet.write(row, col, 'Nom Prénoms',bolth)
            worksheet.write(row, col + 1, 'BANQUE',bolth)
            worksheet.write(row, col+2, 'CODE BANQUE',bolth)
            worksheet.write(row, col + 3, 'CODE AGENCE',bolth)
            worksheet.write(row, col + 4, 'N° COMPTE',bolth)
            worksheet.write(row, col + 5, 'RIB',bolth)
            worksheet.write(row, col + 6, 'NET A PAYER',bolth)
            worksheet.write(row, col + 7, 'NARRATION',bolth)
            
            for bul in lot['slip_ids'].filtered(lambda line: line.modep=='Virement').sorted(key=lambda line: line.employee_id.ordre):
                row+=1
                worksheet.write(row, col, bul.employee_id.name,boltd)
                worksheet.write(row, col+1, bul.employee_id.idbanque.name,boltd) if bul.employee_id.idbanque.name else worksheet.write(row, col+1, '',boltd)
                worksheet.write(row, col+2, bul.employee_id.codeb,boltd) if bul.employee_id.codeb else worksheet.write(row, col+2, '',boltd)
                worksheet.write(row, col+3, bul.employee_id.codeg,boltd) if bul.employee_id.codeg else worksheet.write(row, col+3, '',boltd)
                worksheet.write(row, col+4, bul.employee_id.compteb,boltd) if bul.employee_id.compteb else worksheet.write(row, col+4, '',boltd)
                worksheet.write(row, col+5, bul.employee_id.rib,boltd) if bul.employee_id.rib else worksheet.write(row, col+5, '',boltd)
                worksheet.write(row, col+6, bul.salnetp,boltdsep)
                worksheet.write(row, col+7, lot['nom'])

class PaieIUTSxlsx(models.AbstractModel):
    _name = "report.paie.report_iutsxlsx"
    _inherit="report.report_xlsx.abstract"
    _description = "IUTS excel"
    
    def _get_report_values(self, docids, data=None):
        return{
            "docids":docids,
            "lui":docids.ids,
        }
    def generate_xlsx_report(self, workbook, data, docids):
        
        lines=self._get_report_values(docids)
        selected_records=self.env['hr.payslip.run'].browse(lines['lui'])
        force=[]
        for record in selected_records:
            val={
                "id":record.id,
                "nom":record.name,
                "debut":record.date_start,
                "fin":record.date_end,
                "slip_ids":record.slip_ids,
            }
            force.append(val)
        bolth = workbook.add_format({'bold': 1,'align': 'center','fg_color': 'blue','border': 1, 'color':'white'})
        boltd = workbook.add_format({'border': 1})
        my_format=workbook.add_format({'border': 1,'num_format':'dd/mm/yyyy'})
        boltdsep = workbook.add_format({'border': 1,'num_format':'# ##0'})
        ident = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'yellow'})
        identbo = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'orange'})
        for lot in force:
            worksheet = workbook.add_worksheet(lot['nom'])
            worksheet.set_column(0, 4, 15)
            col=0
            row=1
            worksheet.merge_range(0, col,0,col+5, lot['nom'],identbo)
            worksheet.write(row, col, 'N° Matricule',bolth)
            worksheet.write(row, col + 1, 'Nom Prénoms',bolth)
            worksheet.write(row, col+2, 'Salaire brut',bolth)
            worksheet.write(row, col + 3, 'Total imposable',bolth)
            worksheet.write(row, col + 4, 'Charges',bolth)
            worksheet.write(row, col + 5, 'IUTS dû',bolth)
            
            for bul in lot['slip_ids'].sorted(key=lambda line: line.employee_id.ordre):
                row+=1
                worksheet.write(row, col, bul.employee_id.identification_id,boltd)
                worksheet.write(row, col+1, bul.employee_id.name,boltd)
                worksheet.write(row, col+2, bul.brutp,boltd) if bul.brutp else worksheet.write(row, col+2, '',boltd)
                worksheet.write(row, col+3, bul.biutsp,boltd) if bul.biutsp else worksheet.write(row, col+3, '',boltd)
                worksheet.write(row, col+4, bul.employee_id.children,boltd) if bul.employee_id.children else worksheet.write(row, col+4, '0',boltd)
                worksheet.write(row, col+5, bul.iutsp,boltd) if bul.iutsp else worksheet.write(row, col+5, '',boltd)