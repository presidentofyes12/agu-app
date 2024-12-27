from odoo import models, api
from nostr.key import PrivateKey

class NostrKey(models.AbstractModel):
    _name = 'nostr.key'
    _description = 'Nostr Key Management'

    @api.model
    def get_private_key(self, key_string):
        if key_string.startswith('nsec'):
            return PrivateKey.from_nsec(key_string)
        return PrivateKey(bytes.fromhex(key_string))
