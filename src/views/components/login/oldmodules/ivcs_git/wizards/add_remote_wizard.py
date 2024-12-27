from odoo import models, fields, api

class AddRemoteWizard(models.TransientModel):
    _name = 'ivcs.add.remote.wizard'
    _description = 'Add Remote Repository Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    remote_name = fields.Char(string='Remote Name', default='origin', required=True)
    remote_url = fields.Char(string='Remote URL', required=True)

    def action_add_remote(self):
        self.ensure_one()
        return self.item_id.add_remote(self.remote_url, self.remote_name)
