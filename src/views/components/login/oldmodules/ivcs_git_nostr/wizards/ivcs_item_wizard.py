from odoo import models, fields, api

class IVCSItemCreationWizard(models.TransientModel):
    _name = 'ivcs.item.creation.wizard'
    _description = 'IVCS Item Creation Wizard'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    repo_path = fields.Char('Repository Path', required=True)

    def action_create_ivcs_item(self):
        item = self.env['ivcs.item'].create({
            'name': self.name,
            'description': self.description,
            'repo_path': self.repo_path,
        })
        branch_manager = self.env['ivcs.branch.manager'].create({
            'name': f"Branch Manager for {self.name}",
            'ivcs_item_id': item.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.item',
            'res_id': item.id,
            'view_mode': 'form',
            'target': 'current',
        }
