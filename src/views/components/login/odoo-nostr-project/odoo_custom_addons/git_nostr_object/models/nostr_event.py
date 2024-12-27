# models/nostr_event.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..utils.nostr_websocket_client import NostrWebSocketClient
from nostr.event import Event as NostrEvent
from nostr.key import PrivateKey
import logging
import json
import time

_logger = logging.getLogger(__name__)

class NostrEventObject(models.Model):
    _name = 'nostr.event.object'
    _description = 'Nostr Event Object'

    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    created_at = fields.Integer(string='Created At', required=True)
    signature = fields.Char(string='Signature')
    public_key = fields.Char(string='Public Key', required=True)
    published = fields.Boolean(string='Published', default=False)
    logs = fields.Text(string='Logs')

    def action_publish(self):
        self.ensure_one()
        if self.published:
            raise UserError(_("This event has already been published."))

        start_time = time.time()
        logs = []

        # Get the user's private key
        user = self.env.user
        private_key_nsec = user.nostr_private_key
        if not private_key_nsec:
            raise UserError(_("Nostr private key is not set for the current user."))

        try:
            private_key = PrivateKey.from_nsec(private_key_nsec)
        except Exception as e:
            raise UserError(_("Invalid Nostr private key: %s") % str(e))

        logs.append(f"Key preparation took {time.time() - start_time:.4f} seconds")

        # Create and sign the Nostr event
        event_creation_start = time.time()
        event = NostrEvent(
            kind=self.kind,
            content=self.content,
            tags=json.loads(self.tags) if self.tags else [],
            public_key=private_key.public_key.hex(),
            created_at=int(time.time())
        )
        private_key.sign_event(event)
        logs.append(f"Event creation and signing took {time.time() - event_creation_start:.4f} seconds")

        # Update the record
        self.write({
            'signature': event.signature,
            'public_key': event.public_key,
            'created_at': event.created_at
        })

        relay_urls = [
            'wss://relay.damus.io',
            'wss://nostr-pub.wellorder.net',
            'wss://nostr.mom',
            'wss://nostr.slothy.win',
            'wss://relay.stoner.com'
        ]

        event_data = json.loads(event.to_message())[1]
        websocket_client = NostrWebSocketClient(relay_urls)

        publish_start = time.time()
        try:
            responses, ws_logs = websocket_client.connect_and_publish(event_data)
            logs.extend(ws_logs)
            if any(response[0] == 'OK' for response in responses):
                self.write({'published': True})
                logs.append(f"Nostr event successfully published: {self.id}")
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'title': _("Nostr Event Published"),
                    'message': _("Event successfully published to Nostr network"),
                })
            else:
                error_msg = f"Error publishing Nostr event {self.id}: {responses}"
                logs.append(error_msg)
                raise UserError(_(error_msg))
        except Exception as e:
            error_msg = f"Error publishing Nostr event {self.id}: {e}"
            logs.append(error_msg)
            raise UserError(_(error_msg))
        finally:
            logs.append(f"Publishing process took {time.time() - publish_start:.4f} seconds")

        logs.append(f"Total publish action took {time.time() - start_time:.4f} seconds")
        self.write({'logs': '\n'.join(logs)})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Nostr Event"),
                'message': _("Event published successfully. Check logs for details."),
                'sticky': False,
                'type': 'success',
            }
        }
