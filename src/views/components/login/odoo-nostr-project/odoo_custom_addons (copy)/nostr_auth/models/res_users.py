# File: odoo_custom_addons/nostr_auth/models/res_users.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
import base64

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string='Nostr Public Key')
    nostr_private_key = fields.Char(string='Nostr Private Key')
    nostr_relay_url = fields.Char(string='Nostr Relay URL')

    @api.model_create_multi
    def create(self, vals_list):
        nostr_auth = self.env['nostr.auth.module']
        for vals in vals_list:
            if not vals.get('nostr_private_key'):
                keys = nostr_auth.generate_keypair()
                vals['nostr_private_key'] = keys['private_key']
                vals['nostr_public_key'] = keys['public_key']
        return super(ResUsers, self).create(vals_list)

    @api.constrains('nostr_public_key')
    def _check_nostr_public_key(self):
        for user in self:
            if user.nostr_public_key:
                if not user.nostr_public_key.startswith('npub1'):
                    raise ValidationError("Invalid Nostr public key format. It should start with 'npub1'.")

    @api.model
    def authenticate_nostr(self, public_key, signature, message):
        user = self.search([('nostr_public_key', '=', public_key)], limit=1)
        if user:
            nostr_auth = self.env['nostr.auth.module']
            if nostr_auth.verify_signature(public_key, message, signature):
                return user.id
        return False
