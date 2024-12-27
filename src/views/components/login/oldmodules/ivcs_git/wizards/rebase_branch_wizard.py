# File: odoo_custom_addons/ivcs_git/wizards/rebase_branch_wizard.py

from odoo import models, fields, api

class RebaseBranchWizard(models.TransientModel):
    _name = 'ivcs.rebase.branch.wizard'
    _description = 'Rebase Branch Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    branch_name = fields.Char(string='Branch to Rebase', required=True)
    onto_branch = fields.Char(string='Onto Branch', required=True)

    def action_rebase_branch(self):
        self.ensure_one()
        return self.item_id.rebase_branch(self.branch_name, self.onto_branch)
