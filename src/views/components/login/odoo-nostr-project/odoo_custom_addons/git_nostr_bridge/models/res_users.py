from odoo import models, fields, api
from nostr.key import PrivateKey

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string="Nostr Public Key")
    nostr_private_key = fields.Char(string="Nostr Private Key")
    nostr_relay_url = fields.Char(string="Nostr Relay URL")

    @api.depends('nostr_private_key')
    def _compute_public_key(self):
        for user in self:
            if user.nostr_private_key:
                try:
                    private_key = PrivateKey.from_nsec(user.nostr_private_key)
                    user.nostr_public_key = private_key.public_key.hex()
                except Exception:
                    user.nostr_public_key = False
            else:
                user.nostr_public_key = False

    @api.model
    def create(self, vals):
        if 'nostr_private_key' not in vals or not vals['nostr_private_key']:
            private_key = PrivateKey()
            vals['nostr_private_key'] = private_key.bech32()
        return super(ResUsers, self).create(vals)
