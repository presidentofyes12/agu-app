# wizard/create_nostr_event_wizard.py
from odoo import models, fields, api
import git
import json

class CreateNostrEventWizard(models.TransientModel):
    _name = 'create.nostr.event.wizard'
    _description = 'Create Nostr Event Wizard'

    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
    event_type = fields.Selection([
        ('repo_anchor', 'Repository Anchor'),
        ('branch', 'Branch'),
        ('commit', 'Commit'),
        ('tree', 'Tree'),
        ('blob', 'Blob'),
    ], string='Event Type', required=True)
    commit_message = fields.Text(string='Commit Message')
    branch_name = fields.Char(string='Branch Name')
    file_content = fields.Text(string='File Content')
    file_name = fields.Char(string='File Name')

    def action_create_event(self):
        repo = git.Repo(self.repository_id.path)
        
        if self.event_type == 'commit':
            # Stage all changes
            repo.git.add(A=True)
            # Commit changes
            commit = repo.index.commit(self.commit_message)
            self.repository_id.last_commit = commit.hexsha
            content = json.dumps({
                'type': 'commit',
                'repository': self.repository_id.name,
                'commit_hash': commit.hexsha,
                'message': self.commit_message,
            })
        elif self.event_type == 'branch':
            repo.git.checkout('-b', self.branch_name)
            self.repository_id.branch = self.branch_name
            content = json.dumps({
                'type': 'branch',
                'repository': self.repository_id.name,
                'branch_name': self.branch_name,
            })
        elif self.event_type == 'blob':
            with open(os.path.join(self.repository_id.path, self.file_name), 'w') as f:
                f.write(self.file_content)
            repo.index.add([self.file_name])
            commit = repo.index.commit(f"Add file: {self.file_name}")
            self.repository_id.last_commit = commit.hexsha
            content = json.dumps({
                'type': 'blob',
                'repository': self.repository_id.name,
                'file_name': self.file_name,
                'commit_hash': commit.hexsha,
            })
        
        self.env['nostr.event'].create({
            'name': f"{self.event_type.capitalize()} - {self.repository_id.name}",
            'event_type': self.event_type,
            'content': content,
            'tags': json.dumps([['r', self.repository_id.remote_url]]),
        })

        return {'type': 'ir.actions.act_window_close'}
