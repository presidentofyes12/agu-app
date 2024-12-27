# models/nostr_message.py

from odoo import models, fields

class NostrMessage(models.Model):
    _name = 'nostr.message'
    _description = 'Nostr Message'

    verifier_id = fields.Many2one('nostr.identity.verifier', string='Verifier', required=True, ondelete='cascade')
    content = fields.Text(string='Message Content', required=True)
    processed = fields.Boolean(string='Processed', default=False)
