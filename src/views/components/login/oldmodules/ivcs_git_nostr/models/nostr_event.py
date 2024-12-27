import json
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import traceback
import logging

logger = logging.getLogger(__name__)

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    event_id = fields.Char(string='Event ID', required=True, readonly=True)
    kind = fields.Integer(string='Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    public_key = fields.Char(string='Public Key', required=True)
    created_at = fields.Integer(string='Created At', required=True)
    signature = fields.Char(string='Signature', required=True)

    @api.model
    def create_event(self, kind: int, content: str, tags: list, private_key: str) -> dict:
        try:
            logger.info(f"Creating Nostr event: kind={kind}")
            public_key = self.get_public_key(private_key)
            created_at = int(time.time())
            
            event_data = {
                "kind": kind,
                "created_at": created_at,
                "content": content,
                "tags": tags,
                "public_key": public_key
            }
            
            event_id = self.calculate_event_id(event_data)
            signature = self.sign_event(event_id, private_key)
            
            event_data["id"] = event_id
            event_data["signature"] = signature
            
            self.create(event_data)
            
            logger.info(f"Nostr event created successfully: id={event_id}")
            return event_data
        except Exception as e:
            logger.error(f"Error creating Nostr event: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to create Nostr event: %s") % str(e))

    @api.model
    def get_public_key(self, private_key: str) -> str:
        try:
            private_key_obj = ec.derive_private_key(int(private_key, 16), ec.SECP256K1())
            public_key = private_key_obj.public_key().public_bytes(
                encoding=Encoding.X962,
                format=PublicFormat.UncompressedPoint
            )[1:].hex()
            return public_key
        except Exception as e:
            logger.error(f"Error deriving public key: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to derive public key: %s") % str(e))

    @api.model
    def calculate_event_id(self, event_data: dict) -> str:
        try:
            serialized = json.dumps([
                0,
                event_data['public_key'],
                event_data['created_at'],
                event_data['kind'],
                event_data['tags'],
                event_data['content']
            ], separators=(',', ':'))
            return self.sha256(serialized)
        except Exception as e:
            logger.error(f"Error calculating event ID: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to calculate event ID: %s") % str(e))

    @api.model
    def sign_event(self, event_id: str, private_key: str) -> str:
        try:
            private_key_obj = ec.derive_private_key(int(private_key, 16), ec.SECP256K1())
            signature = private_key_obj.sign(
                bytes.fromhex(event_id),
                ec.ECDSA(hashes.SHA256())
            )
            return signature.hex()
        except Exception as e:
            logger.error(f"Error signing event: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to sign event: %s") % str(e))

    @api.model
    def verify_event(self, event_data: dict) -> bool:
        try:
            public_key_bytes = bytes.fromhex(event_data['public_key'])
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), b'\x04' + public_key_bytes)
            signature = bytes.fromhex(event_data['signature'])
            public_key.verify(signature, bytes.fromhex(event_data['id']), ec.ECDSA(hashes.SHA256()))
            logger.info(f"Event signature verified successfully: id={event_data.get('id')}")
            return True
        except Exception as e:
            logger.warning(f"Event signature verification failed: id={event_data.get('id')}")
            return False

    @api.model
    def sha256(self, data: str) -> str:
        try:
            digest = hashes.Hash(hashes.SHA256())
            digest.update(data.encode())
            return digest.finalize().hex()
        except Exception as e:
            logger.error(f"Error calculating SHA256 hash: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to calculate SHA256 hash: %s") % str(e))

    def to_message(self) -> str:
        try:
            message_dict = {
                "id": self.event_id,
                "kind": self.kind,
                "created_at": self.created_at,
                "content": self.content,
                "tags": json.loads(self.tags) if self.tags else [],
                "public_key": self.public_key,
                "signature": self.signature
            }
            return json.dumps(message_dict)
        except Exception as e:
            logger.error(f"Error converting NostrEvent to message format: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to convert NostrEvent to message format: %s") % str(e))

    @api.model
    def from_message(self, message: str) -> 'NostrEvent':
        try:
            parsed_message_dict = json.loads(message)
            nostr_event = self.create(parsed_message_dict)
            return nostr_event
        except Exception as e:
            logger.error(f"Error creating NostrEvent from message format: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_("Failed to create NostrEvent from message format: %s") % str(e))
