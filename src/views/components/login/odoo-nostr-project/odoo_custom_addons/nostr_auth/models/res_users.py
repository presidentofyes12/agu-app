from odoo import models, fields, api
from odoo.exceptions import AccessDenied, ValidationError
from passlib.context import CryptContext
import logging

_logger = logging.getLogger(__name__)
crypt_context = CryptContext(['pbkdf2_sha512'])

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string='Nostr Public Key', copy=False)
    nostr_private_key = fields.Char(string='Nostr Private Key', copy=False)
    nostr_relay_ids = fields.Many2many('nostr.relay', string='Nostr Relays')
    
    _sql_constraints = [
        ('nostr_public_key_unique', 'unique(nostr_public_key)',
         'Nostr public key must be unique per user!')
    ]

    @api.model
    def _check_credentials(self, password, user_agent_env):
        try:
            super(ResUsers, self)._check_credentials(password, user_agent_env)
        except AccessDenied:
            # Try Nostr authentication if standard auth fails
            if self.nostr_public_key and self.nostr_public_key == self.login:
                valid = crypt_context.verify(password, self.password)
                if valid:
                    return
            raise

    @api.model
    def authenticate(self, db, login, password, user_agent_env):
        try:
            return super(ResUsers, self).authenticate(db, login, password, user_agent_env)
        except AccessDenied:
            if login and login.startswith('npub1'):
                user = self.sudo().search([('nostr_public_key', '=', login)])
                if user and crypt_context.verify(password, user.password):
                    return user.id
            raise

    @api.model
    def create(self, vals):
        if vals.get('nostr_public_key'):
            vals['login'] = vals['nostr_public_key']
            if vals.get('password'):
                vals['password'] = crypt_context.hash(vals['password'])
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        if vals.get('password'):
            vals['password'] = crypt_context.hash(vals['password'])
            vals['password_crypt'] = vals['password']  # Keep both fields in sync
        return super(ResUsers, self).write(vals)

    @api.constrains('nostr_public_key')
    def _check_nostr_public_key(self):
        for user in self:
            if user.nostr_public_key and not user.nostr_public_key.startswith('npub1'):
                raise ValidationError("Nostr public key must start with 'npub1'")
