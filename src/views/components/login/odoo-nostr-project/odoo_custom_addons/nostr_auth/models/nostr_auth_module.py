# File: odoo_custom_addons/nostr_auth/models/nostr_auth_module.py

from odoo import models, api
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
import base64
from bech32 import bech32_encode, bech32_decode, convertbits

class NostrAuthModule(models.AbstractModel):
    _name = 'nostr.auth.module'
    _description = 'Nostr Authentication Module'

    @api.model
    def generate_keypair(self):
        private_key = ec.generate_private_key(ec.SECP256K1())
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
        public_bytes = public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint
        )[1:]
        
        return {
            'private_key': self.bytes_to_nsec(private_bytes),
            'public_key': self.bytes_to_npub(public_bytes)
        }

    @api.model
    def verify_signature(self, public_key, message, signature):
        try:
            public_key_bytes = self.npub_to_bytes(public_key)
            public_key_obj = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), b'\x04' + public_key_bytes)
            signature_bytes = base64.b64decode(signature)
            public_key_obj.verify(
                signature_bytes,
                message.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except:
            return False

    @api.model
    def bytes_to_npub(self, key_bytes):
        data = convertbits(key_bytes[:32], 8, 5)
        return bech32_encode('npub', data)

    @api.model
    def bytes_to_nsec(self, key_bytes):
        data = convertbits(key_bytes[:32], 8, 5)
        return bech32_encode('nsec', data)
        
    @api.model
    def npub_to_bytes(self, npub):
        hrp, data = bech32_decode(npub)
        return bytes(convertbits(data, 5, 8, False))

    @api.model
    def nsec_to_bytes(self, nsec):
        hrp, data = bech32_decode(nsec)
        return bytes(convertbits(data, 5, 8, False))
