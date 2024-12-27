# File: /opt/odoo/custom_addons/git_repository_anchor/models/nostr_event.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.event import Event as NostrLibEvent
from nostr.key import PrivateKey
import json
import time
import logging

_logger = logging.getLogger(__name__)

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    name = fields.Char(string='Name', required=True)
    event_id = fields.Char(string='Event ID', readonly=True)
    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content')
    tags = fields.Text(string='Tags')
    public_key = fields.Char(string='Public Key', readonly=True)
    created_at = fields.Integer(string='Created At', readonly=True)
    signature = fields.Char(string='Signature', readonly=True)
    published = fields.Boolean(string='Published', default=False)
    event_type = fields.Selection([
        ('commit', 'Commit'),
        ('branch', 'Branch'),
        ('tree', 'Tree'),
        ('blob', 'Blob'),
    ], string='Event Type')
    repository_id = fields.Many2one('git.repository', string='Related Repository')

    @api.model
    def create(self, vals):
        try:
            # Generate a new private key for this event
            private_key = PrivateKey()
            public_key = private_key.public_key.hex()
            
            created_at = int(time.time())
            tags = json.loads(vals.get('tags', '[]'))
            
            event = NostrLibEvent(
                kind=vals['kind'],
                content=vals.get('content', ''),
                tags=tags,
                pub_key=public_key,
                created_at=created_at
            )
            
            # Sign the event
            private_key.sign_event(event)
            
            # Update vals with generated data
            vals.update({
                'event_id': event.id,
                'public_key': public_key,
                'created_at': created_at,
                'signature': event.sig
            })
            
            _logger.info(f"Created Nostr event: {event.id}")
        except Exception as e:
            _logger.error(f"Error creating Nostr event: {str(e)}")
            raise UserError(_("Failed to create Nostr event: %s") % str(e))
        
        return super(NostrEvent, self).create(vals)

    @api.model
    def create_and_publish(self, event):
        vals = {
            'name': f"Event {event.id[:8]}",  # Use first 8 characters of event ID as name
            'event_id': event.id,
            'kind': event.kind,
            'content': event.content,
            'tags': json.dumps(event.tags),
            'public_key': event.public_key,
            'created_at': event.created_at,
            'signature': event.sig,
        }
        nostr_event = self.create(vals)
        # Here you would typically publish the event to Nostr relays
        # For demonstration purposes, we'll just log it
        _logger.info(f"Published Nostr event: {event.to_message()}")
        return nostr_event
