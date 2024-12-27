from odoo import http
from odoo.http import request
from nostr.event import Event
import json

class DecentralizedSyncController(http.Controller):

    @http.route('/api/decentralized_sync/publish', type='json', auth='user')
    def publish_event(self, manager_id, content, tags=None):
        manager = request.env['decentralized.sync.manager'].browse(int(manager_id))
        event = manager.publish_event(content, tags)
        return {'status': 'success', 'event_id': event.id}

    @http.route('/api/decentralized_sync/sync_repo', type='json', auth='user')
    def sync_repository(self, manager_id, repo_path):
        manager = request.env['decentralized.sync.manager'].browse(int(manager_id))
        manager.sync_git_repository(repo_path)
        return {'status': 'success', 'message': 'Repository synced and events published'}

    @http.route('/api/decentralized_sync/events', type='json', auth='user')
    def get_events(self, manager_id):
        manager = request.env['decentralized.sync.manager'].browse(int(manager_id))
        # This would typically fetch events from Nostr relays
        # For now, we'll return an empty list
        return {'events': []}
