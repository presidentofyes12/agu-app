# File: odoo_custom_addons/ivcs_git/wizards/merge_branches_wizard.py

from odoo import models, fields, api

class MergeBranchesWizard(models.TransientModel):
    _name = 'ivcs.merge.branches.wizard'
    _description = 'Merge Branches Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    source_branch = fields.Char(string='Source Branch', required=True)
    target_branch = fields.Char(string='Target Branch', required=True)

    def action_merge_branches(self):
        self.ensure_one()
        return self.item_id.merge_branches(self.source_branch, self.target_branch)
