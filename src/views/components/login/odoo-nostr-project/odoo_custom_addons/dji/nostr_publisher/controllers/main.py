from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class NostrPublisherController(http.Controller):
    @http.route('/nostr/publish', type='json', auth='user')
    def publish_event(self, content, kind=1, tags=None):
        try:
            publisher = request.env['nostr.publisher'].sudo().search([('state', '=', 'active')], limit=1)
            if not publisher:
                return {'error': 'No active Nostr Publisher configured'}
            
            event_id = publisher.publish_event(content, kind, tags)
            return {'event_id': event_id}
        except Exception as e:
            _logger.error(f"Error in publish_event: {str(e)}")
            return {'error': 'Failed to publish event'}

    @http.route('/nostr/status', type='json', auth='user')
    def get_status(self):
        try:
            publisher = request.env['nostr.publisher'].sudo().search([], limit=1)
            if not publisher:
                return {'error': 'No Nostr Publisher configured'}
            
            return {
                'name': publisher.name,
                'state': publisher.state,
                'relay_count': publisher.relay_count,
                'last_publish_date': publisher.last_publish_date,
                'total_events_published': publisher.total_events_published,
                'success_rate': publisher.success_rate
            }
        except Exception as e:
            _logger.error(f"Error in get_status: {str(e)}")
            return {'error': 'Failed to retrieve status'}

    @http.route('/nostr/start_listener', type='json', auth='user')
    def start_listener(self):
        try:
            request.env['nostr.publisher'].sudo().start_listening()
            return {'success': True, 'message': 'Nostr listener started'}
        except Exception as e:
            _logger.error(f"Error in start_listener: {str(e)}")
            return {'error': f'Failed to start Nostr listener: {str(e)}'}

    @http.route('/nostr/publish_for_module', type='json', auth='user')
    def publish_for_module(self, module_name, event_type, content, tags=None):
        try:
            publisher = request.env['nostr.publisher'].sudo()
            event_id = publisher.publish_event_for_module(module_name, event_type, content, tags)
            return {'event_id': event_id}
        except Exception as e:
            _logger.error(f"Error in publish_for_module: {str(e)}")
            return {'error': f'Failed to publish event for module: {str(e)}'}

    @http.route('/nostr/test_relays', type='json', auth='user')
    def test_relays(self):
        try:
            publisher = request.env['nostr.publisher'].sudo().search([], limit=1)
            if not publisher:
                return {'error': 'No Nostr Publisher configured'}
            
            publisher.action_test_relays()
            return {'success': True, 'message': 'Relay test initiated'}
        except Exception as e:
            _logger.error(f"Error in test_relays: {str(e)}")
            return {'error': f'Failed to test relays: {str(e)}'}

    @http.route('/nostr/update_active_relays', type='json', auth='user')
    def update_active_relays(self):
        try:
            publisher = request.env['nostr.publisher'].sudo().search([], limit=1)
            if not publisher:
                return {'error': 'No Nostr Publisher configured'}
            
            publisher.update_active_relays()
            return {'success': True, 'message': 'Active relays updated'}
        except Exception as e:
            _logger.error(f"Error in update_active_relays: {str(e)}")
            return {'error': f'Failed to update active relays: {str(e)}'}
