# models/git_repository.py
import os
import git
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository'

    name = fields.Char(string='Name', required=True)
    path = fields.Char(string='Local Path', required=True)
    remote_url = fields.Char(string='Remote URL')
    branch = fields.Char(string='Current Branch', default='main')
    last_commit = fields.Char(string='Last Commit', readonly=True)

    @api.model
    def create(self, vals):
        repo = super(GitRepository, self).create(vals)
        repo._initialize_repository()
        return repo

    def _initialize_repository(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            repo = git.Repo.init(self.path)
            if self.remote_url:
                repo.create_remote('origin', self.remote_url)
            open(os.path.join(self.path, 'README.md'), 'w').close()
            repo.index.add(['README.md'])
            repo.index.commit('Initial commit')
            self.last_commit = repo.head.commit.hexsha

    def action_pull(self):
        repo = git.Repo(self.path)
        origin = repo.remotes.origin
        origin.pull()
        self.last_commit = repo.head.commit.hexsha

    def action_push(self):
        repo = git.Repo(self.path)
        origin = repo.remotes.origin
        origin.push()

    def action_commit(self):
        return {
            'name': _('Create Commit'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.nostr.event.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_repository_id': self.id, 'default_event_type': 'commit'},
        }
