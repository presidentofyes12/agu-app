from odoo import models, fields, api
from .git_object import GitObject

class GitCommit(models.Model):
    _name = 'git.commit'
    _inherit = 'git.object'
    _description = 'Git Commit'

    message = fields.Text(string='Commit Message')
    author = fields.Char(string='Author')
    timestamp = fields.Datetime(string='Timestamp')

    def to_nostr_event(self):
        return self.env['nostr.event.object'].create({
            'kind': 3121,
            'content': self.data,
            'tags': [['sha', self.sha]],
        })

    @api.model
    def create_from_nostr_event(self, event):
        git_commit = GitObject.from_nostr_event(event)
        return self.create({
            'sha': git_commit.sha,
            'data': git_commit.data.decode('utf-8', errors='replace'),
            'message': git_commit.message,
            'author': git_commit.author,
            'timestamp': git_commit.timestamp,
        })
    @api.model
    def create_from_git_commit(self, commit):
        return self.create({
            'sha': commit.hexsha,
            'message': commit.message,
            'author': f"{commit.author.name} <{commit.author.email}>",
            'timestamp': commit.committed_datetime,
            'data': commit.tree.data_stream.read().decode('utf-8', errors='replace'),
        })
