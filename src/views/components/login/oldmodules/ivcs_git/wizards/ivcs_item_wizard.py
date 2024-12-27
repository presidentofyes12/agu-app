from odoo import models, fields, api

class IVCSItemCreationWizard(models.TransientModel):
    _name = 'ivcs.item.creation.wizard'
    _description = 'IVCS Item Creation Wizard'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')

    def action_create_ivcs_item(self):
        item = self.env['ivcs.item'].create({
            'name': self.name,
            'description': self.description,
        })
        item.ensure_version()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.item',
            'res_id': item.id,
            'view_mode': 'form',
            'target': 'current',
        }
