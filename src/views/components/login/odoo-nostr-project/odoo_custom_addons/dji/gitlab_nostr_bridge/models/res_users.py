# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.key import PrivateKey
import secrets
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_private_key = fields.Char(string="Nostr Private Key", copy=False)
    nostr_public_key = fields.Char(string="Nostr Public Key", compute='_compute_nostr_public_key', store=True)
    gitlab_username = fields.Char(string="GitLab Username")
    gitlab_email = fields.Char(string="GitLab Email")
    gitlab_user_id = fields.Integer(string="GitLab User ID")

    @api.depends('nostr_private_key')
    def _compute_nostr_public_key(self):
        for user in self:
            if user.nostr_private_key:
                try:
                    private_key = PrivateKey.from_nsec(user.nostr_private_key)
                    user.nostr_public_key = private_key.public_key.bech32()
                except Exception as e:
                    _logger.error(f"Error computing public key for user {user.id}: {str(e)}")
                    user.nostr_public_key = False
            else:
                user.nostr_public_key = False

    @api.model
    def create(self, vals):
        if 'nostr_private_key' not in vals:
            vals['nostr_private_key'] = self._generate_nostr_key()
        user = super(ResUsers, self).create(vals)
        user.sync_gitlab_user()
        return user

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'login' in vals or 'email' in vals:
            self.sync_gitlab_user()
        return res

    def _generate_nostr_key(self):
        private_key = PrivateKey()
        return private_key.bech32()

    def action_generate_nostr_key(self):
        self.ensure_one()
        private_key = PrivateKey()
        self.nostr_private_key = private_key.bech32()
        self._compute_nostr_public_key()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Nostr Key Generated"),
                'message': _("A new Nostr key pair has been generated."),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_clear_nostr_key(self):
        self.ensure_one()
        self.nostr_private_key = False
        self._compute_nostr_public_key()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Nostr Key Cleared"),
                'message': _("The Nostr key pair has been cleared."),
                'type': 'warning',
                'sticky': False,
            }
        }

    def sync_gitlab_user(self):
        for user in self:
            gl = self.env['gitlab_nostr_bridge.create.commit.wizard']._get_gitlab_client()
            try:
                gitlab_user = gl.users.list(username=user.login)[0]
                user.write({
                    'gitlab_username': gitlab_user.username,
                    'gitlab_email': gitlab_user.email,
                    'gitlab_user_id': gitlab_user.id,
                })
                _logger.info(f"GitLab user information synced for user {user.login}")
            except Exception as e:
                _logger.warning(f"Failed to sync GitLab user for {user.login}: {str(e)}")

    def action_sync_gitlab_user(self):
        self.ensure_one()
        self.sync_gitlab_user()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("GitLab User Synced"),
                'message': _("GitLab user information has been synchronized."),
                'type': 'success',
                'sticky': False,
            }
        }
