from odoo import models, api
from .nostr_auth import verify_token
from .shared_session import get_session

class CustomAuth(models.AbstractModel):
    _name = 'custom.auth'

    @api.model
    def authenticate(self, token):
        if verify_token(token):
            session_data = get_session(token)
            if session_data:
                user = self.env['res.users'].sudo().search([('nostr_public_key', '=', session_data['publicKey'])])
                if user:
                    return user.id
        return False
