# File: odoo_custom_addons/ivcs_git/wizards/switch_branch_wizard.py

from odoo import models, fields, api

class SwitchBranchWizard(models.TransientModel):
    _name = 'ivcs.switch.branch.wizard'
    _description = 'Switch Branch Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    branch_name = fields.Char(string='Branch Name', required=True)

    def action_switch_branch(self):
        self.ensure_one()
        return self.item_id.switch_branch(self.branch_name)
