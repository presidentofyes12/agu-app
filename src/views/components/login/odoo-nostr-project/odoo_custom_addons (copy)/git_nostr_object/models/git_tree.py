from odoo import models, fields, api
from .git_object import GitObject

class GitTree(models.Model):
    _name = 'git.tree'
    _inherit = 'git.object'
    _description = 'Git Tree'

    def to_nostr_event(self):
        return self.env['nostr.event.object'].create({
            'kind': 3122,
            'content': self.data,
            'tags': [['sha', self.sha]],
        })

    @api.model
    def create_from_nostr_event(self, event):
        git_tree = GitObject.from_nostr_event(event)
        return self.create({
            'sha': git_tree.sha,
            'data': git_tree.data.decode('utf-8', errors='replace'),
        })
