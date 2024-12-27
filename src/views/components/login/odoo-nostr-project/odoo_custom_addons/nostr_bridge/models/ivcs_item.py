# File: odoo_custom_addons/nostr_bridge/models/ivcs_item.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import git
import os
import logging
from nostr.key import PrivateKey

_logger = logging.getLogger(__name__)

class IVCSItem(models.Model):
    _inherit = 'ivcs.item'

    nostr_private_key = fields.Char(string="Nostr Private Key")

    def _create_nostr_event_and_publish(self, commit):
        if not self.nostr_private_key:
            self.nostr_private_key = PrivateKey().hex()
            self.sudo().write({'nostr_private_key': self.nostr_private_key})

        private_key = PrivateKey(bytes.fromhex(self.nostr_private_key))
        nostr_manager = self.env['nostr.event.manager']
        event = nostr_manager.create_git_event(commit, private_key)

        relay_urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
        for relay_url in relay_urls:
            if relay_url.strip():
                success = nostr_manager.publish_event_sync(event, relay_url.strip())
                if success:
                    _logger.info(f"Successfully published event to {relay_url}")
                else:
                    _logger.warning(f"Failed to publish event to {relay_url}")

    def sync_repository(self):
        result = super(IVCSItem, self).sync_repository()
        if result.get('type') == 'ir.actions.client' and result['params']['type'] == 'success':
            repo = git.Repo(self.repo_path)
            latest_commit = repo.head.commit
            self._create_nostr_event_and_publish(latest_commit)
        return result

    def create_file(self, filename, content):
        result = super(IVCSItem, self).create_file(filename, content)
        if result.get('type') == 'ir.actions.client' and result['params']['type'] == 'success':
            repo = git.Repo(self.repo_path)
            latest_commit = repo.head.commit
            self._create_nostr_event_and_publish(latest_commit)
        return result

    @api.model
    def create(self, vals):
        item = super(IVCSItem, self).create(vals)
        repo = git.Repo(item.repo_path)
        initial_commit = repo.head.commit
        item._create_nostr_event_and_publish(initial_commit)
        return item
