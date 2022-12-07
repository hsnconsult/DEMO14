# -*- coding: utf-8 -*-
from odoo import models, fields, api
from . import enlettres
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'
  
    objet = fields.Char("Objet")
    secure_sequence_id = fields.Many2one('ir.sequence',help='Sequence to use to ensure the securisation of data',check_company=True)
  
    @api.onchange('name', 'highest_name')
    def _onchange_name_warning(self):
        if self.name and self.name != '/' and self.name <= (self.highest_name or ''):
            #self.show_name_warning = True
            self.show_name_warning = False
        else:
            self.show_name_warning = False

    #Permettre la selection de tout type de journal            
    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            domain = [('company_id', '=', m.company_id.id), ('type', '=', journal_type)]
            #m.suitable_journal_ids = self.env['account.journal'].search(domain)
            m.suitable_journal_ids = self.env['account.journal'].search([])
        
    def _post(self, soft=True):
        to_post = super(AccountMove,self)._post()
        to_post.set_name()
        return to_post
        
    def set_name(self):
        for move in self:
            if move.name == '/':
                new_name = False
                journal = move.journal_id
                if journal.sequence_id:
                   sequence = journal.sequence_id
                   new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                else:
                   raise UserError('Vous devez definir une sequence pour ce journal.')
                if new_name:
                    move.name = new_name 
    @api.depends('name')                    
    def get_namev(self):
        for record in self:
            record.namev = record.name        
    name = fields.Char(string='Number', required=True, copy=False, default='/')
    namev = fields.Char(string='Number', compute='get_namev')
    ligne_avance = fields.One2many('etatper.avance','invoice_id','Avances')
    def _compute_name(self):
        self.filtered(lambda m: not m.name).name = '/'
class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = "account.journal"

    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence',
        help="This field contains the information related to the numbering of the journal entries of this journal.", required=True, copy=False)
    refund_sequence_id = fields.Many2one('ir.sequence', string='Credit Note Entry Sequence',
        help="This field contains the information related to the numbering of the credit note entries of this journal.", copy=False)
    refund_sequence = fields.Boolean(string='Dedicated Credit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and credit notes made from this journal", default=False)       
class saleorder(models.Model):
    _inherit = 'sale.order' 
 
    def _prepare_invoice(self):
        invoice_vals = super(saleorder,self)._prepare_invoice()
        invoice_vals['objet'] = self.objet
        invoice_vals['ligne_avance'] = self.ligne_avance
        return invoice_vals        
    livrables = fields.Text("LIVRABLES")
    objet = fields.Text("Objet")
    ligne_avance = fields.One2many('etatper.avance','order_id','Avances')
    dateeff = fields.Date('Date effective',default=fields.Date.context_today)
    
class saleorderline(models.Model):
    _inherit = 'sale.order.line' 
    def _prepare_invoice_line(self, **optional_values):
        res = super(saleorderline,self)._prepare_invoice_line()
        res['unite'] = self.unite
        return res        
    unite = fields.Char("Unité") 
    
class AccountMoveline(models.Model):
    _inherit = 'account.move.line'
    
    unite = fields.Char("Unité") 
    
class Avance(models.Model):
    _name = 'etatper.avance'

    @api.onchange('order_id.amount_total','taux')
    def get_montant(self):
        for record in self:
            record.montant = record.order_id.amount_total*record.taux/100
    @api.onchange('order_id.amount_total','montant')
    def get_taux(self):
        for record in self:
            record.taux = (record.montant/record.order_id.amount_total)*100 if record.order_id.amount_total!=0 else 0
    def set_name(self):
        for avance in self:
            if avance.name == '/':
                new_name = False
                journal = self.env['account.journal'].search([('type','=','sale')])[0]
                if journal.sequence_id:
                   sequence = journal.sequence_id
                   new_name = sequence.with_context(ir_sequence_date=avance.date).next_by_id()
                else:
                   raise UserError('Vous devez definir une sequence pour ce journal.')
                if new_name:
                    avance.name = new_name
    def valider(self):
        self.set_name()
        self.write({'state':'valide'})
    def brouillon(self):
        self.write({'state':'brouillon'})
    date = fields.Date('Date')
    order_id = fields.Many2one('sale.order', 'Order')
    invoice_id = fields.Many2one('account.move', 'Move')
    name = fields.Char('Avance', default='/')
    taux = fields.Float('Taux(%)')
    montant = fields.Float('Montant')
    state = fields.Selection(selection=[('brouillon', 'Brouillon'),('valide', 'Validé')], string='Etat', required=True, readonly=True, copy=False, tracking=True, default='brouillon')
class Company(models.Model):
    _name = "res.company"
    _description = 'Companies'
    _inherit = "res.company"

    def compute_amount_text(self,nombre):
        return enlettres.convlettres(nombre)
