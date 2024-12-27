from odoo import models, fields, api
import logging
from nostr.key import PrivateKey
from nostr.event import Event
from nostr.relay_manager import RelayManager
import git
import os

_logger = logging.getLogger(__name__)

class DecentralizedNostrSyncManager(models.Model):
    _name = 'decentralized.sync.manager'
    _description = 'Decentralized Nostr Sync Manager'

    name = fields.Char(string='Name', required=True)
    relay_urls = fields.Text(string='Relay URLs', required=True)
    private_key = fields.Char(string='Private Key')
    public_key = fields.Char(string='Public Key', compute='_compute_public_key')

    @api.depends('private_key')
    def _compute_public_key(self):
        for record in self:
            if record.private_key:
                private_key = PrivateKey.from_nsec(record.private_key)
                record.public_key = private_key.public_key.bech32()
            else:
                record.public_key = False

    def initialize_nostr(self):
        if not self.private_key:
            private_key = PrivateKey()
            self.private_key = private_key.bech32()
        
        self.relay_manager = RelayManager()
        for url in self.relay_urls.split(','):
            self.relay_manager.add_relay(url.strip())
        self.relay_manager.open_connections()

    def publish_event(self, content, tags=None):
        if not hasattr(self, 'relay_manager'):
            self.initialize_nostr()

        private_key = PrivateKey.from_nsec(self.private_key)
        event = Event(content=content, tags=tags or [])
        private_key.sign_event(event)
        
        self.relay_manager.publish_event(event)
        return event

    def sync_git_repository(self, repo_path):
        repo = git.Repo(repo_path)
        if not repo.remotes:
            raise ValueError('No remote repository configured')

        origin = repo.remotes.origin
        origin.fetch()
        
        current_branch = repo.active_branch
        if f'origin/{current_branch.name}' not in repo.refs:
            origin.push(current_branch)
        else:
            origin.pull(current_branch)

        for commit in repo.iter_commits(f'{current_branch.name}@{{u}}..{current_branch.name}'):
            self.publish_event(
                content=f"New commit: {commit.hexsha}",
                tags=[['c', commit.hexsha], ['t', 'git_commit']]
            )

    @api.model
    def create(self, vals):
        manager = super(DecentralizedNostrSyncManager, self).create(vals)
        manager.initialize_nostr()
        return manager

    def write(self, vals):
        result = super(DecentralizedNostrSyncManager, self).write(vals)
        if 'relay_urls' in vals:
            self.initialize_nostr()
        return result
