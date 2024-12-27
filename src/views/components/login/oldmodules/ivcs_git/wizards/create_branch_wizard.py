# File: odoo_custom_addons/ivcs_git/wizards/create_branch_wizard.py

from odoo import models, fields, api

class CreateBranchWizard(models.TransientModel):
    _name = 'ivcs.create.branch.wizard'
    _description = 'Create Branch Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    branch_name = fields.Char(string='Branch Name', required=True)

    def action_create_branch(self):
        self.ensure_one()
        return self.item_id.create_branch(self.branch_name)
