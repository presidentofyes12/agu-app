from odoo import models, fields, api
from .git_object import GitObject

class GitBlob(models.Model):
    _name = 'git.blob'
    _inherit = 'git.object'
    _description = 'Git Blob'

    def to_nostr_event(self):
        return self.env['nostr.event.object'].create({
            'kind': 3123,
            'content': self.data,
            'tags': [['sha', self.sha]],
        })

    @api.model
    def create_from_nostr_event(self, event):
        git_blob = GitObject.from_nostr_event(event)
        return self.create({
            'sha': git_blob.sha,
            'data': git_blob.data.hex(),
        })
