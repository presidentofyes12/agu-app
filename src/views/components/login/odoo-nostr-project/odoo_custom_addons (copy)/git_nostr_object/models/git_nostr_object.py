# models/git_nostr_event.py
from odoo import models, fields, api
from utils.nostr_websocket_client import NostrWebSocketClient
from nostr.event import Event as NostrEvent
import logging
import time
import json

_logger = logging.getLogger(__name__)

class GitNostrEventObject(models.Model):
    _name = 'git_nostr.event.object'
    _description = 'Git Nostr Event Object'

    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    created_at = fields.Integer(string='Created At', required=True)
    signature = fields.Char(string='Signature', required=True)
    public_key = fields.Char(string='Public Key', required=True)
    published = fields.Boolean(string='Published', default=False)

    def action_publish(self):
        """
        Publish the Nostr event to the configured relays.
        """
        relay_urls = [
            'wss://relay.damus.io',
            'wss://nostr-pub.wellorder.net',
            'wss://nostr.mom',
            'wss://nostr.slothy.win',
            'wss://relay.stoner.com'
        ]

        event_data = {
            'kind': self.kind,
            'content': self.content,
            'tags': self.tags,
            'created_at': self.created_at,
            'pubkey': self.public_key,
            'sig': self.signature,
        }

        websocket_client = NostrWebSocketClient(relay_urls)

        try:
            responses = websocket_client.connect_and_publish(event_data)
            if all(response[0] == 'OK' and response[2] for response in responses):
                self.write({'published': True})
                _logger.info(f"Nostr event successfully published: {self.id}")
            else:
                self.write({'published': False})
                _logger.error(f"Error publishing Nostr event {self.id}: {responses}")
        except Exception as e:
            self.write({'published': False})
            _logger.error(f"Error publishing Nostr event {self.id}: {e}")

    def to_nostr_event(self):
        try:
            tags = json.loads(self.tags) if self.tags else []
        except json.JSONDecodeError:
            _logger.warning(f"Invalid JSON in tags for event {self.id}. Using empty tags list.")
            tags = []

        return NostrEvent(
            kind=self.kind,
            content=self.content,
            tags=tags,
            public_key=self.public_key,
            created_at=self.created_at,
            sig=self.signature
        )
