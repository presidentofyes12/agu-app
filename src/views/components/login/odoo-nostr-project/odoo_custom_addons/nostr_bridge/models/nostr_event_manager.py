from odoo import models, fields, api
import json
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import logging
import git

_logger = logging.getLogger(__name__)

class NostrEventManager(models.AbstractModel):
    _name = 'nostr.event.manager'
    _description = 'Nostr Event Manager'

    @api.model
    def create_event(self, content, tags, private_key):
        private_key_obj = PrivateKey.from_nsec(private_key)
        event = Event(kind=1, content=content, tags=tags)
        private_key_obj.sign_event(event)
        return event.to_json()

    @api.model
    def get_public_key(self, private_key):
        private_key_obj = ec.derive_private_key(int(private_key, 16), ec.SECP256K1())
        public_key = private_key_obj.public_key()
        return public_key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.UncompressedPoint
        )[1:].hex()

    @api.model
    def calculate_event_id(self, event_data):
        serialized = json.dumps([
            0,
            event_data['pubkey'],
            event_data['created_at'],
            event_data['kind'],
            event_data['tags'],
            event_data['content']
        ], separators=(',', ':'))
        return self.sha256(serialized)

    @api.model
    def sign_event(self, event_data, private_key):
        private_key_obj = ec.derive_private_key(int(private_key, 16), ec.SECP256K1())
        signature = private_key_obj.sign(
            bytes.fromhex(event_data['id']),
            ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    @api.model
    def sha256(self, data):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data.encode())
        return digest.finalize().hex()

    @api.model
    def create_git_event(self, repo_path, commit_hash):
        repo = git.Repo(repo_path)
        commit = repo.commit(commit_hash)
        
        content = json.dumps({
            "action": "commit",
            "message": commit.message,
            "author": commit.author.name,
            "email": commit.author.email,
            "date": commit.authored_datetime.isoformat()
        })
        
        tags = [
            ["t", "commit"],
            ["h", commit_hash],
            ["n", repo.active_branch.name],
            ["m", commit.author.name],
            ["v", "1.0"],
            ["r", repo.remotes.origin.url if repo.remotes else ""],
            ["p", self.env.user.nostr_public_key],
            ["d", commit.message],
            ["s", "success"]
        ]
        
        event = self.create_event(content, tags, self.env.user.nostr_private_key)
        self.publish_event(event)
        return event

    def sync_with_decentralized_manager(self, event):
        sync_managers = self.env['decentralized.sync.manager'].search([])
        for manager in sync_managers:
            program = self.env['decentralized.sync.program'].search([
                ('manager_id', '=', manager.id),
                ('content', '=', event['content'])
            ], limit=1)

            if not program:
                program = self.env['decentralized.sync.program'].create({
                    'manager_id': manager.id,
                    'creator_id': self.env['decentralized.sync.creator'].search([], limit=1).id,
                    'content': event['content'],
                    'version': 1,
                    'size': 0.5  # Arbitrary size
                })

            manager.propagate_update(program)

    @api.model
    def publish_event(self, event):
        sync_managers = self.env['decentralized.sync.manager'].search([])
        for manager in sync_managers:
            manager.publish_event(event['content'], event['tags'])
        return True

    @api.model
    def get_events(self, filters=None):
        nostr_adapter = self.env['nostr.adapter']
        return nostr_adapter.get_events(filters)
