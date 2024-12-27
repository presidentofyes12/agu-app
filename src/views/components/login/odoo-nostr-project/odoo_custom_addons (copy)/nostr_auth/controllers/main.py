# controllers/main.py
from odoo import http
from odoo.http import request
import json

class NostrAuthController(http.Controller):
    @http.route('/web/nostr/authenticate', type='json', auth='none')
    def authenticate(self, public_key, signature, message):
        uid = request.env['res.users'].sudo().authenticate_nostr(public_key, signature, message)
        if uid:
            request.session.authenticate(request.session.db, uid, public_key)
            return {'success': True, 'uid': uid}
        return {'success': False, 'error': 'Authentication failed'}
