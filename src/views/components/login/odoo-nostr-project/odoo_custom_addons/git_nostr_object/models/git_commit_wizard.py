from odoo import models, fields, api

class GitCommitWizard(models.TransientModel):
    _name = 'git.commit.wizard'
    _description = 'Git Commit Wizard'

    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
    message = fields.Text(string='Commit Message', required=True)
    file_data = fields.Text(string='File Content')
    file_name = fields.Char(string='File Name')

    def action_create_commit(self):
        repo = self.repository_id
        with open(f"{repo.path}/{self.file_name}", 'w') as f:
            f.write(self.file_data)
        commit = repo.create_commit(self.message, [self.file_name])
        return {'type': 'ir.actions.act_window_close'}
