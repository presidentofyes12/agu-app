from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import asyncio
from nostr.bech32 import bech32_decode, convertbits

_logger = logging.getLogger(__name__)

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    event_id = fields.Char(string='Event ID', required=True, index=True)
    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    public_key = fields.Char(string='Public Key', required=True)
    created_at = fields.Integer(string='Created At', required=True)
    signature = fields.Char(string='Signature', required=True)
    published = fields.Boolean(string='Published', default=False)

    _sql_constraints = [
        ('unique_event_id', 'UNIQUE(event_id)', 'Event ID must be unique!')
    ]

    @api.model
    def _convert_to_hex(self, key):
        if key.startswith('npub') or key.startswith('nsec'):
            hrp, data = bech32_decode(key)
            if data is None:
                raise ValueError(f"Invalid bech32 key: {key}")
            decoded = convertbits(data, 5, 8, False)
            return bytes(decoded).hex()
        return key  # Assume it's already in hex format if not bech32

    @api.model
    def process_incoming_events(self):
        _logger.info("Starting to process incoming Nostr events")
        
        # Get active relays from Nostr Publisher
        publisher = self.env['nostr.publisher'].search([('state', '=', 'active')], limit=1)
        if not publisher:
            _logger.warning("No active Nostr Publisher found")
            return

        relay_urls = publisher.relay_ids.filtered(lambda r: r.is_active).mapped('url')
        if not relay_urls:
            _logger.warning("No active relay URLs found")
            return

        _logger.info(f"Processing events from {len(relay_urls)} relays")

        asyncio.run(self._fetch_and_process_events(relay_urls))

        _logger.info("Finished processing incoming Nostr events")

    @api.model
    def create(self, vals):
        if 'public_key' in vals:
            vals['public_key'] = self._convert_to_hex(vals['public_key'])
        if not self._validate_event(vals):
            raise UserError(_("Invalid Nostr event data"))
        return super(NostrEvent, self).create(vals)

    def write(self, vals):
        if 'public_key' in vals:
            vals['public_key'] = self._convert_to_hex(vals['public_key'])
        return super(NostrEvent, self).write(vals)

    @api.model
    def _validate_event(self, event_data):
        required_fields = ['event_id', 'kind', 'content', 'public_key', 'created_at', 'signature']
        for field in required_fields:
            if field not in event_data or not event_data[field]:
                _logger.error(f"Missing or empty required field: {field}")
                return False
        
        try:
            json.loads(event_data.get('tags', '[]'))
        except json.JSONDecodeError:
            _logger.error("Invalid JSON format for tags")
            return False

        # Add more validation as needed, e.g., signature verification
        return True

    def mark_as_published(self):
        self.ensure_one()
        self.published = True

    def get_json_representation(self):
        self.ensure_one()
        return {
            "id": self.event_id,
            "pubkey": self.public_key,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": json.loads(self.tags or '[]'),
            "content": self.content,
            "sig": self.signature
        }
