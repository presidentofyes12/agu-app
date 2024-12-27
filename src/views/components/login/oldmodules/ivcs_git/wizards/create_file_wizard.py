from odoo import models, fields, api

class IVCSCreateFileWizard(models.TransientModel):
    _name = 'ivcs.create.file.wizard'
    _description = 'Create File Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    filename = fields.Char(string='Filename', required=True)
    content = fields.Text(string='File Content', required=True)

    def action_create_file(self):
        self.ensure_one()
        return self.item_id.create_file(self.filename, self.content)
