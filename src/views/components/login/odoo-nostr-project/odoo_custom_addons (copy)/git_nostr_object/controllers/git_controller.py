from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GitController(http.Controller):

    @http.route('/git_nostr_object/traverse_repo', type='json', auth='user')
    def traverse_repo(self, repo_id):
        try:
            repo = request.env['git.repository'].browse(repo_id)
            repo.traverse_and_publish()
            return {'status': 'success'}
        except Exception as e:
            _logger.exception("Error traversing repository")
            return {'status': 'error', 'message': str(e)}

    @http.route('/git_nostr_object/publish_event', type='json', auth='user')
    def publish_event(self, event_id):
        try:
            event = request.env['git_nostr.event.object'].browse(event_id)
            event.action_publish()
            return {'status': 'success'}
        except Exception as e:
            _logger.exception("Error publishing Nostr event")
            return {'status': 'error', 'message': str(e)}
