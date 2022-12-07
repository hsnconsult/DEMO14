# -*- coding: utf-8 -*-
import time
import math
from datetime import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta



class paie_categorie(models.Model):
    _name = "paie.categorie"
    _description = "Categorie"


    name = fields.Char('Categorie')
    indlog = fields.Float('Ind Logement', digits=(16,0))
    indtrans = fields.Float('Ind Transport', digits=(16,0))

class paie_echelon(models.Model):
    _name = "paie.echelon"
    _description = "Echelon"

    name = fields.Char('Echelon')

class paie_grillemere(models.Model):
    _name = "paie.grillemere"
    _description = "Grille mere"

    name = fields.Date('Date grille')
    ligne_grille = fields.One2many('paie.grille', 'idgrillemere', 'Grilles')
    
class paie_grille(models.Model):
    _name = "paie.grille"
    _description = "Grille"

    @api.depends('categorie','echelon')
    def get_name(self):
        for record in self:
            record.name = record.categorie.name+'-'+record.echelon.name

    idgrillemere = fields.Many2one('paie.grillemere', 'Grille mere')
    categorie = fields.Many2one('paie.categorie', 'Categorie')
    echelon = fields.Many2one('paie.echelon', 'Echelon')
    name = fields.Char('Classe', compute='get_name', store=True)
    salaire = fields.Float('Salaire', digits=(16,0))

class paie_pret(models.Model):
    _name = 'paie.pret'
    _description = 'Pret'

    def valider(self):
        trouve = self.env['paie.pret'].search([('employee_id','=',self.employee_id.id),('state','=','encours')])
        if trouve:
           raise UserError('Cet employé a déjà un pret en cours')
        for record in self.ligne_tableaupret:
            record.write({'state':'impaye'})
        self.write({'state':'encours'})
    def cloturer(self):
        for record in self.ligne_tableaupret:
            if record.state == 'impaye':
               record.write({'state':'annule'})
        self.write({'state':'cloture'})
    @api.depends('ligne_tableaupret.montantech','ligne_tableaupret.state')
    def get_remb(self):
        for record in self:
            mt = 0
            capr = 0
            for recordfil in record.ligne_tableaupret:
                if recordfil.state=='paye':
                   mt = mt + recordfil.montantech
                   capr = capr + recordfil.montantech - recordfil.intdu
            record.rembourse = mt
            record.capremb = capr
            record.caprest = record.montant - capr
    @api.depends('ligne_tableaupret.montantech')
    def get_montantdu(self):
        for record in self:
            montant = 0
            for recordfil in record.ligne_tableaupret:
                montant = montant + recordfil.montantech
            record.montantdu = montant
    @api.depends('montant','rembourse')
    def get_rap(self):
        for record in self:
            record.rap = record.montantdu - record.rembourse


    def gentab(self):
        commands = [(2, line_id.id, False) for line_id in self.ligne_tableaupret]
        self.write({'ligne_tableaupret': commands})
        if self.taux != 0:
            tauxper = (self.taux/12)/100
            traite = round(self.montant*(tauxper/(1-pow(1+tauxper,self.nbech*(-1)))),0)
        else:
            tauxper = 0
            traite = round(self.montant/self.nbech,0)
        commands = []
        capdu = self.montant
        mydate = datetime.strptime(str(self.dateprem),'%Y-%m-%d')
        for i in range (0,self.nbech):
            intdu = round(capdu*tauxper,0)
            vals = {
              'dateech': datetime(mydate.year,mydate.month,1)+relativedelta(months=i+1,days=-1),
              'montantech': traite,
              'intdu':intdu,
              'capdu':capdu,
              'montantremb': 0,
              'caprest':capdu-traite,
              'numech':i+1,
             }
            if i == self.nbech-1 and self.taux==0:
              #raise UserError(i)
              vals = {
              'dateech': datetime(mydate.year,mydate.month,1)+relativedelta(months=i+1,days=-1),
              'montantech': self.montant - round(self.montant/self.nbech,0)*(self.nbech-1),
              'intdu':intdu,
              'capdu':self.montant - round(self.montant/self.nbech,0)*(self.nbech-1),
              'montantremb': 0,
              'caprest':0,
              'numech':i+1,
             }
            commands.append((0, False, vals))
            capdu = capdu - traite
        self.write({'ligne_tableaupret': commands,'traite':traite})
        return True       

    @api.depends('dateprem','nbech')
    def get_dateder(self):
        for record in self:
            fin = False
            for recordfil in record.ligne_tableaupret:
                fin = recordfil.dateech
            record.dateder = fin if fin else False
            #mydate = datetime.strptime(record.dateprem,'%Y-%m-%d') if record.dateprem else False
            #record.dateder = datetime(mydate.year,mydate.month,1)+relativedelta(record.nbech,days=-1) if mydate else False	    
    employee_id = fields.Many2one('hr.employee', 'Employé')
    objet = fields.Char('Objet')
    type = fields.Selection([('pret','Prêt'),('acompte','Acompte'),('avance','Avance')], string='Type', required=True)
    date = fields.Date('Date du pret')
    dateprem = fields.Date('Date Début', required=True)
    dateder = fields.Date('Date Fin', compute='get_dateder')
    montant = fields.Float('Montant accordé', digits=(16,0), required=True)
    nbech = fields.Integer('Nombre d\'échéances', required=True)
    taux = fields.Float('Taux')
    montantdu = fields.Float('Montant dû', compute='get_montantdu', store=True, digits=(16,0))
    rembourse = fields.Float('Remboursé', compute='get_remb', digits=(16,0))
    capremb = fields.Float('Capital remboursé', compute='get_remb', digits=(16,0))
    caprest = fields.Float('Capital restant dû', compute='get_remb', digits=(16,0))    
    rap = fields.Float('Reste à payer', compute='get_rap', digits=(16,0))
    traite = fields.Float('Traite', digits=(16,0))
    ligne_tableaupret = fields.One2many('paie.tableaupret','idpret','Ligne tableau')
    state = fields.Selection([('brouillon', 'Brouillon'),('encours', 'En cours'),('cloture', 'Clôturé')],'Etat', track_visibility='onchange', default = 'brouillon')
    

class paie_tableaupret(models.Model):
    _name = 'paie.tableaupret'
    _description = 'Tableau Pret'

    @api.depends('idinput.amount')
    def get_montantremb(self):
        for record in self:
            record.montantremb = record.idinput.amount
    idpret = fields.Many2one('paie.pret', 'Pret', required=True)
    dateech = fields.Date('Date Echeance')
    montantech = fields.Float('Montant', digits=(16,0))
    intdu = fields.Float('Intérêt dû', digits=(16,0))
    capdu = fields.Float('Capital dû', digits=(16,0))
    montantremb = fields.Float('Remboursé', compute='get_montantremb', digits=(16,0), store=True)
    ref = fields.Char('Référence')
    idinput = fields.Many2one('hr.payslip.input','Input')
    state = fields.Selection([('brouillon', 'Brouillon'),('impaye', 'Impayée'),('paye', 'Payée'),('annule', 'Annulée')],'Etat', track_visibility='onchange', default = 'brouillon')
    numech = fields.Integer('N°')
    caprest = fields.Float('Capital restant', digits=(16,0))


class paie_absence(models.Model):
    _name = 'paie.absence'
    _description = 'Absences'

    @api.depends('nbjabsence')
    def get_nbjtravail(self):
        for record in self:
            record.nbjtravail = 30 - record.nbjabsence if record.nbjabsence<=30 else 0

    idlot = fields.Many2one('hr.payslip.run', 'Lot')
    idemploye = fields.Many2one('hr.employee', 'Employé', required=True)
    nbjabsence = fields.Integer('Nombre de jours absentés', required=True)
    nbjtravail = fields.Integer('Nombre de jours travaillés', compute='get_nbjtravail', store=True)
    
class paie_pretsimp(models.Model):
    _name = 'paie.pretsimp'
    _description = 'Pret simplifie'
    
    @api.depends('ligne_remb.traite')
    def get_remb(self):
        for record in self:
            mt = 0
            for recordfil in record.ligne_remb:
                mt = mt+recordfil.traite
            record.rembourse = mt
    @api.depends('montant','rembourse')
    def get_rap(self):
        for record in self:
            record.rap = record.montant - record.rembourse
            
        
    employee_id = fields.Many2one('hr.employee', 'Employé')
    objet = fields.Char('Objet')
    type = fields.Selection([('pret','Prêt'),('acompte','Acompte'),('avance','Avance')], string='Type', required=True)
    date = fields.Date('Date du pret')
    montant = fields.Float('Montant accordé', digits=(16,0), required=True)
    rembourse = fields.Float('Remboursé', compute='get_remb', digits=(16,0))
    rap = fields.Float('Reste à payer', compute='get_rap', digits=(16,0))
    traite = fields.Float('Traite', digits=(16,0))
    state = fields.Selection([('impaye', 'Impayé'),('paye', 'Payé')],'Etat', track_visibility='onchange', default = 'impaye')
    ligne_remb = fields.One2many('hr.payslip','idpret','Remboursements')
