from odoo import models, fields, api
import base64
import os
import git

class IVCSFile(models.Model):
    _name = 'ivcs.file'
    _description = 'IVCS File'

    name = fields.Char('File Name', required=True)
    item_id = fields.Many2one('ivcs.item', string='Item', required=True)
    version_id = fields.Many2one('ivcs.version', string='Version', required=True)
    file_content = fields.Binary('File Content', attachment=True)
    file_type = fields.Selection([
        ('text', 'Text'),
        ('binary', 'Binary')
    ], string='File Type', required=True)

    @api.model
    def create(self, vals):
        file = super(IVCSFile, self).create(vals)
        file._add_to_repository()
        return file

    def _add_to_repository(self):
        repo = git.Repo(self.item_id.repo_path)
        file_path = os.path.join(self.item_id.repo_path, self.name)
        
        if self.file_type == 'text':
            content = base64.b64decode(self.file_content).decode('utf-8')
            with open(file_path, 'w') as f:
                f.write(content)
        else:
            content = base64.b64decode(self.file_content)
            with open(file_path, 'wb') as f:
                f.write(content)

        repo.index.add([self.name])
        commit = repo.index.commit(f"Add file: {self.name}")
        self.version_id.commit_hash = commit.hexsha
