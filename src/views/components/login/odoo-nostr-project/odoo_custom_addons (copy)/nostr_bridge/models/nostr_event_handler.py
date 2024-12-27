import json
from odoo import api, models

class NostrEventHandler(models.AbstractModel):
    _name = 'nostr.event.handler'
    _description = 'Nostr Event Handler'

    @api.model
    def handle_event(self, event):
        content = json.loads(event.content)
        if event.kind == 1:  # Text note
            self._handle_message(content)
        elif event.kind == 7:  # Reaction
            self._handle_reaction(content)

    def _handle_message(self, content):
        self.env['mail.message'].create({
            'body': content['body'],
            'author_id': self._get_author_id(content['author']),
            'model': content['channel'],
            'res_id': content['res_id'],
        })

    def _handle_reaction(self, content):
        # Implement reaction handling (e.g., likes, emojis)
        pass

    def _get_author_id(self, author_name):
        partner = self.env['res.partner'].search([('name', '=', author_name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({'name': author_name})
        return partner.id
