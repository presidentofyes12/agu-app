from odoo import models, fields, api

class NostrRelay(models.Model):
    _name = 'nostr.relay'
    _description = 'Nostr Relay'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
