from odoo import models, fields, api
from odoo.exceptions import AccessDenied
from nostr.key import PrivateKey

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string='Nostr Public Key')
    nostr_private_key = fields.Char(string='Nostr Private Key')

    @api.model
    def authenticate_nostr(self, public_key, signature, message):
        user = self.search([('nostr_public_key', '=', public_key)], limit=1)
        if user:
            try:
                priv_key = PrivateKey(bytes.fromhex(user.nostr_private_key))
                pub_key = priv_key.public_key
                if pub_key.verify_signed_message_signature(signature, message):
                    return user.id
            except Exception as e:
                _logger.error(f"Nostr authentication error: {str(e)}")
        return False

    @api.model
    def create_nostr_user(self, public_key):
        private_key = PrivateKey()
        public_key = private_key.public_key.hex()
        return self.create({
            'name': f'Nostr User {public_key[:8]}',
            'login': public_key,
            'nostr_public_key': public_key,
            'nostr_private_key': private_key.hex(),
        })
