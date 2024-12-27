from odoo import http
from odoo.http import request
import json
from nostr.event import Event
from nostr.key import PrivateKey

class NostrController(http.Controller):

    @http.route('/nostr/authenticate', type='json', auth='public')
    def authenticate(self, public_key, signature, message):
        User = request.env['res.users'].sudo()
        user_id = User.authenticate_nostr(public_key, signature, message)
        if user_id:
            request.session.authenticate(request.db, user_id, public_key)
            return {'success': True, 'uid': user_id}
        return {'success': False, 'error': 'Authentication failed'}

    @http.route('/nostr/publish', type='json', auth='user')
    def publish_event(self, event_data):
        nostr_adapter = request.env['nostr.adapter'].sudo().get_adapter()
        try:
            nostr_adapter.publish_event(event_data)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/nostr/subscribe', type='json', auth='user')
    def subscribe_to_events(self, filters):
        nostr_adapter = request.env['nostr.adapter'].sudo().get_adapter()
        try:
            def callback(event):
                # Process the event, e.g., create a message in Odoo
                request.env['nostr.event.handler'].sudo().handle_event(event)

            nostr_adapter.subscribe_to_events(filters, callback)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/nostr/get_public_key', type='json', auth='user')
    def get_public_key(self):
        user = request.env.user
        return {'public_key': user.nostr_public_key}

    @http.route('/nostr/create_event', type='json', auth='user')
    def create_event(self, kind, content, tags=None):
        user = request.env.user
        private_key = PrivateKey.from_nsec(user.nostr_private_key)
        event = Event(kind=kind, content=json.dumps(content), tags=tags or [])
        event.sign(private_key.hex())
        return {
            'id': event.id,
            'pubkey': event.public_key,
            'created_at': event.created_at,
            'kind': event.kind,
            'tags': event.tags,
            'content': event.content,
            'sig': event.signature,
        }
