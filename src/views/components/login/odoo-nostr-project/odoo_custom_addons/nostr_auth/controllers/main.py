# controllers/main.py
from odoo import http
from odoo.http import request
import json
from odoo.addons.web.controllers.main import Home
from odoo.exceptions import AccessDenied

class NostrAuthController(Home):
    @http.route('/web/login', type='http', auth="none", methods=['GET', 'POST'], website=True)
    def web_login(self, redirect=None, **kw):
        try:
            # First try Nostr authentication
            if request.httprequest.method == 'POST':
                username = request.params.get('login', '')
                password = request.params.get('password', '')
                
                if username and password and (username.startswith('npub1') or username.startswith('nsec1')):
                    uid = request.env['res.users'].sudo().search([
                        ('nostr_public_key', '=', username)
                    ]).id
                    
                    if uid:
                        request.session.authenticate(request.db, username, password)
                        return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
        except AccessDenied:
            pass
            
        return super(NostrAuthController, self).web_login(redirect=redirect, **kw)

    @http.route('/web/nostr/authenticate', type='json', auth='none')
    def authenticate(self, public_key, signature, message):
        uid = request.env['res.users'].sudo().authenticate_nostr(public_key, signature, message)
        if uid:
            request.session.authenticate(request.session.db, uid, public_key)
            return {'success': True, 'uid': uid}
        return {'success': False, 'error': 'Authentication failed'}
