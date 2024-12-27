from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
from cryptography.fernet import Fernet
import logging
import secrets
from nostr.key import PrivateKey
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import bech32

_logger = logging.getLogger(__name__)

def hex_to_nostr_key(hex_key, prefix):
    # Convert hex to bytes
    data = bytes.fromhex(hex_key)
    
    # Convert to 5-bit words
    words = bech32.convertbits(data, 8, 5)
    
    # Encode with bech32
    encoded = bech32.bech32_encode(prefix, words)
    
    return encoded

class NostrIdentity(models.Model):
    _name = 'nostr.identity'
    _description = 'Nostr Identity'

    name = fields.Char(string='Name', required=True)
    public_key = fields.Char(string='Public Key (hex)', readonly=True)
    private_key = fields.Char(string='Private Key (hex)', readonly=True)
    public_key_bech32 = fields.Char(string='Public Key (npub)', readonly=True, compute='_compute_bech32_keys')
    private_key_bech32 = fields.Char(string='Private Key (nsec)', readonly=True, compute='_compute_bech32_keys')
    relay_urls = fields.Text(string='Relay URLs')
    profile_data = fields.Text(string='Profile Data')

    @api.model
    def create(self, vals):
        if 'public_key' not in vals or 'private_key' not in vals:
            try:
                private_key = PrivateKey()
                public_key = private_key.public_key
                vals['private_key'] = private_key.hex()
                vals['public_key'] = public_key.hex()
            except Exception as e:
                _logger.error(f"Failed to generate Nostr keys: {str(e)}")
                raise UserError(_("Failed to generate Nostr keys: %s") % str(e))
        return super(NostrIdentity, self).create(vals)

    @api.depends('public_key', 'private_key')
    def _compute_bech32_keys(self):
        for record in self:
            if record.public_key:
                record.public_key_bech32 = hex_to_nostr_key(record.public_key, "npub")
            else:
                record.public_key_bech32 = False
            
            if record.private_key:
                record.private_key_bech32 = hex_to_nostr_key(record.private_key, "nsec")
            else:
                record.private_key_bech32 = False

    def get_private_key(self):
        self.ensure_one()
        try:
            encryption_key = self.env['ir.config_parameter'].sudo().get_param('nostr.encryption_key')
            if not encryption_key:
                raise UserError(_("Encryption key not found. Unable to decrypt private key."))
            
            fernet = Fernet(encryption_key.encode())
            decrypted_private_key = fernet.decrypt(base64.b64decode(self.encrypted_private_key))
            return PrivateKey(bytes.fromhex(decrypted_private_key.decode()))
        except Exception as e:
            _logger.error(f"Failed to decrypt private key: {str(e)}")
            raise UserError(_("Failed to decrypt private key: %s") % str(e))

    def get_public_key_bech32(self):
        return self.public_key_bech32
