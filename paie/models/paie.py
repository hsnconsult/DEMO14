# -*- coding: utf-8 -*-
import time
import math
from datetime import datetime, date, time
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import pytz


class hr_contract(models.Model):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = "hr.contract"

    @api.onchange('idcategorie','idechelon')
    def onchangecatech(self):
        for record in self:
            record.wage = self.env['paie.grille'].search([('categorie','=',self.idcategorie.id),('echelon','=',self.idechelon.id)])[0].salaire if self.env['paie.grille'].search([('categorie','=',self.idcategorie.id),('echelon','=',self.idechelon.id)]) else 0
            record.indlog = record.idcategorie.indlog
            record.indtrans = record.idcategorie.indtrans
    cat_id = fields.Many2one('hr.employee.category', 'Catégorie')
    sursal = fields.Integer("Sursalaire")
    indlog = fields.Integer("Indemnité de logement")
    indfonc = fields.Integer("Indemnité de fonction")
    indtrans = fields.Integer("Indeminté de transport")
    indcai = fields.Integer("Indeminité de caisse")
    indpou = fields.Integer("Indeminité de poussière")
    indsuj = fields.Integer("Indeminité de sujetion")
    indresp = fields.Integer("Indeminité de responsabilité")
    indsal = fields.Integer("Indeminité de salissure")
    indfor = fields.Integer("Indeminité speciale")
    indast = fields.Integer("Indeminité d\'astreinte")
    bruti = fields.Float("Brut initial")
    neti = fields.Float("Net imposable initial")
    chargesali = fields.Float("Charge sal. initial")
    chargepati = fields.Float("Charge pat. initial")
    heureti = fields.Float("Heures travaillés initial")
    heuresupi = fields.Float("Heures sup initial")
    congeaci = fields.Float("Congés acquis initial")
    congepi = fields.Float("Congés pris initial")
    idcategorie = fields.Many2one('paie.categorie', 'Catégorie')
    idechelon = fields.Many2one('paie.echelon', 'Echelon')
    typeemp = fields.Selection([('cadre','Cadre'),('employe','Employe')], 'Type Employé', required=True)
    mutuelle = fields.Float('Retenue Mutuelle', digits=(16,0))



class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _description = 'Salary rule'
    _inherit = "hr.salary.rule"

    ref = fields.Char('Référence')

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = "hr.payslip"
  
    def initpret(self):
        if self.idech:
           self.idech.write({'state':'impaye'}) 
        self.write({'traite':0,'intdu':0,'capdu':0,'idech':False,'type':''})
    def setpret(self):
        idech = self.env['paie.tableaupret'].search([('idpret.employee_id','=',self.employee_id.id),('dateech','=',self.date_to),('state','=','impaye')])[0] if self.env['paie.tableaupret'].search([('idpret.employee_id','=',self.employee_id.id),('dateech','=',self.date_to),('state','=','impaye')]) else False
        if idech:
           self.write({'traite':idech.montantech,'intdu':idech.intdu,'capdu':idech.capdu,'idech':idech.id,'type':idech.idpret.type})
           idech.write({'state':'paye'})
           
    def setpretsimp(self):
        idpret = self.env['paie.pretsimp'].search([('employee_id','=',self.employee_id.id),('state','=','impaye')])[0] if self.env['paie.pretsimp'].search([('employee_id','=',self.employee_id.id),('state','=','impaye')]) else False
        if idpret:
           self.write({'traite':idpret.traite,'idpret':idpret.id,'type':idpret.type})
    
    @api.onchange('employee_id')
    def onchange_emp(self):
        #raise UserError(self.employee_id)
        for record in self:
            contract = self.env['hr.contract'].search([('state','=','open'),('employee_id','=',record.employee_id.id)])[0] if record.employee_id else False
            record.contract_id = contract.id if contract else False
            record.struct_id = self.env['hr.payroll.structure'].search([])[0].id if self.env['hr.payroll.structure'].search([]) else False
    @api.onchange('date_to')
    def onchange_dateto(self):
        for record in self:
            record.datep = record.date_to

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        wketype = self.struct_id.type_id.default_work_entry_type_id
        wketype_id = self.struct_id.type_id.default_work_entry_type_id.id
        #hours_per_day = self._get_worked_day_lines_hours_per_day()
        #work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        #work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        #biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        #add_days_rounding = 0
        #for work_entry_type_id, hours in work_hours_ordered:
        #    work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
        #    days = round(hours / hours_per_day, 5) if hours_per_day else 0
        #    if work_entry_type_id == biggest_work:
        #        days += add_days_rounding
        #    day_rounded = self._round_days(work_entry_type, days)
        #    add_days_rounding += (days - day_rounded)
        attendance_line = {
                'sequence': wketype.sequence,
                'work_entry_type_id': wketype_id,
                'number_of_days': 30,
                'number_of_hours': 173.33,
          }
        res.append(attendance_line)
        return res
        
    @api.depends('date_from','contract_id.date_start')
    def get_anc(self):
        for record in self:
            if record.contract_id and record.date_to:
                #debut = datetime.strptime(record.contract_id.date_start+' 00:00','%Y-%m-%d %H:%M')
                #fin = datetime.strptime(record.date_to+' 00:00','%Y-%m-%d %H:%M')
                debut = record.contract_id.date_start
                fin = record.date_from
                record.ancannee = relativedelta(fin,debut).years
                record.ancmois = relativedelta(fin,debut).months
    @api.depends('line_ids.total','worked_days_line_ids.number_of_days','input_line_ids.amount','line_ids')
    def get_rub(self):
        for record in self:
            netp = 0
            iutsp = 0
            
            for recordfil in record.line_ids:
                if recordfil.code == 'SBRUT':
                   record.brutp = round(recordfil.total,0)
                if recordfil.code == 'BIUTS' or recordfil.code == 'BIUTSC':
                   netp = netp+round(recordfil.total,0)
                if recordfil.code == 'CHARGESAL':
                   record.chargesalp = round(recordfil.total,0)
                if recordfil.code == 'CHARGEPAT':
                   record.chargepatp = round(recordfil.total,0)
                if recordfil.code == 'SBASE':
                   record.sbasep = round(recordfil.total,0)
                if recordfil.code == 'ANC':
                   record.ancp = round(recordfil.total,0)
                if recordfil.code == 'SURSAL':
                   record.sursalp = round(recordfil.total,0)
                if recordfil.code == 'INDLOG':
                   record.logementp = round(recordfil.total,0)
                if recordfil.code == 'INDTRANS':
                   record.transportp = round(recordfil.total,0)
                if recordfil.code == 'INDFONC':
                   record.fonctionp = round(recordfil.total,0)
                if recordfil.code == 'IUTS' or recordfil.code == 'IUTSC':
                   iutsp = iutsp+round(recordfil.total,0)
                if recordfil.code == 'AVANCE':
                   record.avp = round(recordfil.total,0)
                if recordfil.code == 'PRETS':
                   record.pretp = round(recordfil.total,0)
                if recordfil.code == 'RETMUT':
                   record.mutp = round(recordfil.total,0)
                if recordfil.code == 'NETP':
                   record.salnetp = round(recordfil.total,0)
                if recordfil.code == 'SURSAL':
                   record.sursalp = round(recordfil.total,0)
                if recordfil.code == 'TPA':
                   record.tpa = round(recordfil.total,0)
                if recordfil.code == 'BIUTS':
                   record.biutsp = round(recordfil.total,0)
                if recordfil.code == 'BCNSS':
                   record.bcnss = round(recordfil.total,0)
                if recordfil.code == 'INDFOR':
                   record.indforp = round(recordfil.total,0)
                   
            record.netp = netp
            record.iutsp = iutsp
            for recordfill in record.worked_days_line_ids:
                if recordfill.code == 'WORK100':
                   record.heuretp = recordfill.number_of_days*173.33/30
            tothsup = 0
            for recordfilll in record.input_line_ids:
                if 'HSUP' in recordfilll.code:
                   tothsup = tothsup + recordfilll.amount
                if recordfilll.code == 'CONGEP':
                   record.congepp = recordfilll.amount 
                record.heuresupp = tothsup
            record.congeacp = 2.5
            record.congerestp = 0
            

    @api.depends('brutp','netp','chargesalp','chargepatp','heuretp','heuresupp','congeacp','congepp','congerestp')
    def get_ruba(self):
        for record in self:
            #bula = self.env['hr.payslip'].search([('date_to','ilike',record.date_to[0:4]),('employee_id','=',record.employee_id.id)])
            bula = self.env['hr.payslip'].search([('date_to','ilike',record.date_to.year),('employee_id','=',record.employee_id.id)])
            bruta = record.contract_id.bruti
            neta = record.contract_id.neti
            chargesala = record.contract_id.chargesali
            chargepata = record.contract_id.chargepati
            heureta = record.contract_id.heureti
            heuresupa = record.contract_id.heuresupi
            congeaca = record.contract_id.congeaci
            congepa = record.contract_id.congepi
            congeresta = 0
            for recordf in bula:
                bruta = bruta+recordf.brutp
                neta = neta+recordf.netp
                chargesala = chargesala+recordf.chargesalp
                chargepata = chargepata+recordf.chargepatp
                heureta = heureta+recordf.heuretp
                heuresupa = heuresupa+recordf.heuresupp
                congeaca = congeaca+recordf.congeacp
                congepa = congepa+recordf.congepp
                congeresta = congeaca - congepa
                if congeresta < 0:
                   congeresta = 0 
            record.bruta = bruta
            record.neta = neta
            record.chargesala = chargesala
            record.chargepata = chargepata
            record.heureta = heureta
            record.heuresupa = heuresupa
            record.congeaca = congeaca
            record.congepa = congepa
            record.congeresta = congeresta
    @api.onchange('employee_id')
    def get_modep(self):
        for record in self:
            record.modep = record.employee_id.modep      
    idpret = fields.Many2one('paie.pretsimp', 'Pret')
    idech = fields.Many2one('paie.tableaupret','Echeance')
    traite = fields.Float('Traite', digits=(16,0))
    intdu = fields.Float('Interêt', digits=(16,0))
    capdu = fields.Float('Capital', digits=(16,0))
    type = fields.Selection([('pret','Prêt'),('acompte','Acompte'),('avance','Avance')], string='Type')
    ancannee = fields.Integer('Ancienneté années', compute='get_anc', store = True)
    ancmois = fields.Integer('Ancienneté mois', compute='get_anc', store = True)
    modep = fields.Selection([('Chèque','Chèque'),('Virement','Virement'),('Espèces','Espèces')],string='Mode de paiement', default='Virement')
    datep = fields.Date('Date paiement')
    
    sbasep = fields.Float('Base Période', compute='get_rub', store = True)
    ancp = fields.Float('Ancienneté Période', compute='get_rub', store = True)
    sursalp = fields.Float('Sursalaire Période', compute='get_rub', store = True)
    logementp = fields.Float('Logement Période', compute='get_rub', store = True)
    transportp = fields.Float('Transport Période', compute='get_rub', store = True)
    fonctionp = fields.Float('Fonction Période', compute='get_rub', store = True)
    brutp = fields.Float('Brut Période', compute='get_rub', store = True)
    chargesalp = fields.Float('Charge salariale', compute='get_rub', store = True)
    chargepatp = fields.Float('Charge patronale', compute='get_rub', store = True)
    tpa = fields.Float('TPA', compute='get_rub', store = True)
    iutsp = fields.Float('IUTS Période', compute='get_rub', store = True)
    pretp = fields.Float('Pret Période', compute='get_rub', store = True)
    mutp = fields.Float('Mutuelle Période', compute='get_rub', store = True)
    avp = fields.Float('Avance Période', compute='get_rub', store = True)
    netp = fields.Float('Net imposable', compute='get_rub', store = True)
    salnetp = fields.Float('Salaire net', compute='get_rub', store = True)
    indforp = fields.Float('Indemnite speciale', compute='get_rub', store = True)
    
    biutsp = fields.Float('Base IUTS', compute='get_rub', store = True)
    bcnss = fields.Float('Base CNSS', compute='get_rub', store = True)
    
    heuretp = fields.Float('Heures travaillées', compute='get_rub', store = True)
    heuresupp = fields.Float('Heures sup', compute='get_rub', store = True)
    
    congeacp = fields.Float('Congés acquis', compute='get_rub', store = True)
    congepp = fields.Float('Congés pris', compute='get_rub', store = True)
    congerestp = fields.Float('Congés restant', compute='get_rub', store = True)
    
    bruta = fields.Float('Brut Année', compute='get_ruba', store = True)
    neta = fields.Float('Net imposable', compute='get_ruba', store = True)
    chargesala = fields.Float('Charge salariale', compute='get_ruba', store = True)
    chargepata = fields.Float('Charge patronale', compute='get_ruba', store = True)
    heureta = fields.Float('Heures travaillées', compute='get_ruba', store = True)
    heuresupa = fields.Float('Heures sup', compute='get_ruba', store = True)
    congeaca = fields.Float('Congés acquis', compute='get_ruba', store = True)
    congepa = fields.Float('Congés pris', compute='get_ruba', store = True)
    congeresta = fields.Float('Congés restant', compute='get_ruba', store = True) 
    

class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'
    _inherit = "hr.payroll.structure"


    tauxa = fields.Selection([('25%','25%'),('20%','20%')], string = 'Taux abattement IUTS')

class hr_payslip_run(models.Model):
    _name = "hr.payslip.run"
    _description = "Lot de bulletin"
    _inherit = "hr.payslip.run"
    
    def fixe_jourtravail(self):
        for record in self.ligne_absence:
            trouve = 0
            for bulletin in self.slip_ids:
                if record.idemploye.id == bulletin.employee_id.id:
                   trouve = 1
                   for wkdays in bulletin.worked_days_line_ids:
                       wkdays.write({'number_of_days':record.nbjtravail})
            if trouve == 0:
               raise UserError('Bulletins non retrouvés pour certains employés absents')
    def calcule_feuille(self):
        self.fixe_jourtravail()
        for record in self.slip_ids:
            record.modep = record.employee_id.modep
            #record.struct_id = self.env['hr.payroll.structure'].search([])[0].id
            record.initpret()
            record.setpret()
            record.compute_sheet()
        return True
    def brouillon(self):
        for record in self.slip_ids:
            record.write({'state':'draft'})
        self.write({'state':'draft','compta':False})
        #for record in self.move_id.line_ids:
        #    record.unlink()
        #for record in self.move_id.invoice_line_ids:
        #    record.unlink()
        self.move_id.unlink()
       

    
        
    def get_rub(self):
        for record in self:
            sbase=panc=sursal=indlog=indtrans=indfonc=cnssemp=cnsspat=tpa=iuts=pret=mut=av=salnet=indfor=0
            for recordfil in record.slip_ids:
                sbase=sbase+round(recordfil.sbasep,0)
                panc=panc+round(recordfil.ancp,0)
                sursal=sursal+round(recordfil.sursalp,0)
                indfonc=indfonc+round(recordfil.fonctionp,0)
                indtrans=indtrans+round(recordfil.transportp,0)
                indlog=indlog+round(recordfil.logementp,0)
                cnssemp = cnssemp+round(recordfil.chargesalp,0)
                cnsspat = cnsspat+round(recordfil.chargepatp,0)
                tpa=tpa+round(recordfil.tpa,0)
                iuts=iuts+round(recordfil.iutsp,0)
                pret=pret+round(recordfil.pretp,0)
                mut=mut+round(recordfil.mutp,0)
                av=av+round(recordfil.avp,0)
                salnet=salnet+round(recordfil.salnetp,0)
                indfor=indfor+round(recordfil.indforp,0)
            record.sbase = round(sbase,0)
            record.panc = round(panc,0)
            record.sursal = round(sursal,0)
            record.indfonc = round(indfonc,0)
            record.indlog = round(indlog,0)
            record.indtrans = round(indtrans,0)
            record.cnssemp = round(cnssemp,0)
            record.cnsspat = round(cnsspat,0)
            record.tpa = round(tpa,0)
            record.iuts = round(iuts,0)
            record.pret = round(pret,0)
            record.mut = round(mut,0)
            record.av = round(av,0)
            record.salnet = round(salnet,0)
            record.indfor = round(indfor,0)
            
            
            
    def comptabiliser(self):
        am = self.env['account.move']
        aml = []
        company = self.env.user.company_id 
        iutscalcule = self.sbase+self.panc+self.indfonc + self.indtrans + self.indlog - self.cnssemp - self.pret - self.salnet 
        if self.tpa != 0: 
           vals1 = {
                'account_id':company.tpad.id,
                'name' : 'T.P.A - Paie '+self.name,
                'debit': self.tpa,
                'credit': 0,
                }
           aml.append((0, False, vals1))
        if self.sursal != 0: 
           vals0 = {
                'account_id':company.sursal.id,
                'name' : 'Sursalaire - Paie '+self.name,
                'debit': self.sursal,
                'credit': 0,
                }
           aml.append((0, False, vals0))
        if self.sbase != 0: 
           vals2 = {
                'account_id':company.sbase.id,
                'name' : 'Salaire de base - Paie '+self.name,
                'debit': self.sbase,
                'credit': 0,
                }
           aml.append((0, False, vals2))
        if self.panc != 0: 
           vals3 = {
                'account_id':company.panc.id,
                'name' : 'Prime d\'ancienneté - Paie '+self.name,
                'debit': self.panc,
                'credit': 0,
                }
           aml.append((0, False, vals3))
        if self.indfonc != 0: 
           vals4 = {
                'account_id':company.indfonc.id,
                'name' : 'Indemnité de fonction - Paie '+self.name,
                'debit': self.indfonc,
                'credit': 0,
                }
           aml.append((0, False, vals4))
        if self.indtrans != 0: 
           vals5 = {
                'account_id':company.indtrans.id,
                'name' : 'Indemnité de transport - Paie '+self.name,
                'debit': self.indtrans,
                'credit': 0,
                }
           aml.append((0, False, vals5))
        if self.indlog != 0: 
           vals6 = {
                'account_id':company.indlog.id,
                'name' : 'Indemnité de logement - Paie '+self.name,
                'debit': self.indlog,
                'credit': 0,
                }
           aml.append((0, False, vals6))
        if self.cnsspat != 0: 
           vals7 = {
                'account_id':company.cnsspat.id,
                'name' : 'Charge patronale - Paie '+self.name,
                'debit': self.cnsspat,
                'credit': 0,
                }
           aml.append((0, False, vals7))
        if self.pret != 0: 
           vals8 = {
                'account_id':company.pret.id,
                'name' : 'Total prêts - Paie '+self.name,
                'debit': 0,
                'credit': self.pret,
                }
           aml.append((0, False, vals8))
        if self.salnet != 0: 
           vals9 = {
                'account_id':company.salnet.id,
                'name' : 'Salaire net à payer (sans arrondi) - Paie '+self.name,
                'debit': 0,
                'credit': self.salnet,
                }
           aml.append((0, False, vals9))
        if self.cnssemp != 0: 
           vals10 = {
                'account_id':company.cnss.id,
                'name' : 'TOTAL CNSS - Paie '+self.name,
                'debit': 0,
                'credit': self.cnssemp+self.cnsspat,
                }
           aml.append((0, False, vals10))
        if self.iuts != 0: 
           vals11 = {
                'account_id':company.iuts.id,
                'name' : 'I.U.T.S - Paie '+self.name,
                'debit': 0,
                'credit': iutscalcule,
                }
           aml.append((0, False, vals11))
        if self.tpa != 0: 
           vals12 = {
                'account_id':company.tpac.id,
                'name' : 'TPA - Paie '+self.name,
                'debit': 0,
                'credit': self.tpa,
                }
           aml.append((0, False, vals12))
        amc = am.create({'journal_id':company.journalpaie.id,'date':self.date_end,'ref':'Traitement de la paie: '+self.name})
        for record in amc:
            record.write({'line_ids':aml})
            #record.post()
        self.write({'compta':True})
        self.write({'move_id': amc.id})
        return True
    compta = fields.Boolean("Comptabilisé", default = False)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    sbase = fields.Float('Salaire de base', compute='get_rub')
    sursal = fields.Float('Sursalaire', compute='get_rub')
    panc = fields.Float('Prime Ancienneté', compute='get_rub')
    indfonc = fields.Float('Indeminité de fonction', compute='get_rub')
    indtrans = fields.Float('Indemnité de transport', compute='get_rub')
    indlog = fields.Float('Indemnité de logement', compute='get_rub')
    cnssemp = fields.Float('CNSS', compute='get_rub')
    cnsspat = fields.Float('CNSS Patronale', compute='get_rub')
    tpa = fields.Float('TPA', compute='get_rub')
    iuts = fields.Float('IUTS', compute='get_rub')
    pret = fields.Float('Prêts', compute='get_rub')
    mut = fields.Float('Mutuelle', compute='get_rub')
    av = fields.Float('Avance', compute='get_rub')
    salnet = fields.Float('Salaire net à payer', compute='get_rub')
    ligne_absence = fields.One2many('paie.absence','idlot','Ligne absence')
    indfor = fields.Float('Indemnité speciale', compute='get_rub')
    
    
    
    
class Employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    categorie = fields.Char('Catégorie')
    echelon = fields.Char('Echelon')
    secsoc = fields.Char('N° Sécurité sociale')
    title = fields.Many2one('res.partner.title')
    ordre = fields.Integer('Ordre')
    partner_id = fields.Many2one('res.partner')
    idbanque = fields.Many2one('res.bank')
    codeb = fields.Char('Code Banque')
    codeg = fields.Char('Code Guichet')
    compteb = fields.Char('N° Compte')
    rib = fields.Char('RIB')
    modep = fields.Selection([('Chèque','Chèque'),('Virement','Virement'),('Espèces','Espèces')],string='Mode de paiement', default='Virement')
    pret = fields.One2many('paie.pret','employee_id', string='Prets')
    pretsimp = fields.One2many('paie.pretsimp','employee_id', string='Prets')
    

class Company(models.Model):
    _name = "res.company"
    _description = 'Companies'
    _inherit = "res.company"

    journalpaie = fields.Many2one('account.journal',string='Journal des salaires')
    sbase = fields.Many2one('account.account','Salaire de base')
    panc = fields.Many2one('account.account','Prime Ancienneté') 
    sursal = fields.Many2one('account.account','Sursalaire')    
    indfonc = fields.Many2one('account.account','Indeminité de fonction')
    indtrans = fields.Many2one('account.account','Indemnité de transport')
    indlog = fields.Many2one('account.account','Indemnité de logement')
    cnss = fields.Many2one('account.account','Total CNSS')
    cnsspat = fields.Many2one('account.account','CNSS patronale')
    tpac = fields.Many2one('account.account','TPA crédit')
    tpad = fields.Many2one('account.account','TPA débit')
    iuts = fields.Many2one('account.account','IUTS')
    pret = fields.Many2one('account.account','Prêts')
    mut = fields.Many2one('account.account','Mutuelle')
    av = fields.Many2one('account.account','Avance')
    salnet = fields.Many2one('account.account','Salaire net à payer')
    indfor = fields.Many2one('account.account','Indemnité speciale')
    
class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _inherit = 'hr.payslip.employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            #if outside:
            #    raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.", contract.employee_id.name))    
    
