from odoo import models, fields, api

class GitObject(models.AbstractModel):
    _name = 'git.object'
    _description = 'Git Object'

    sha = fields.Char(string='SHA', required=True)
    data = fields.Text(string='Data', required=True)

    def to_nostr_event(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    @api.model
    def create_from_nostr_event(self, event):
        raise NotImplementedError("This method should be implemented by subclasses")
