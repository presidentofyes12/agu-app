from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.event import Event
from nostr.key import PrivateKey
import json
import logging
import time
import git

_logger = logging.getLogger(__name__)

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    event_id = fields.Char(string='Event ID', required=True)
    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    public_key = fields.Char(string='Public Key')
    created_at = fields.Integer(string='Created At', required=True)
    signature = fields.Char(string='Signature', required=True)
    published = fields.Boolean(string='Published', default=False)
    name = fields.Char(string='Name')
    event_type = fields.Selection([
        ('repo_anchor', 'Repository Anchor'),
        ('branch', 'Branch'),
        ('commit', 'Commit'),
        ('tree', 'Tree'),
        ('blob', 'Blob'),
    ], string='Event Type')

    def create_and_publish(self, event):
        event_model = self._get_event_model(event.kind)
        if event_model:
            nostr_event = event_model.from_json(event.to_json())
            nostr_event.publish_event()
            return nostr_event
        else:
            return super(NostrEvent, self).create_and_publish(event)

    def _get_event_model(self, kind):
        if kind == 31228:
            return self.env['nostr.event.repository.anchor']
        elif kind == 31227:
            return self.env['nostr.event.branch']
        elif kind == 3121:
            return self.env['nostr.event.commit']
        elif kind == 3122:
            return self.env['nostr.event.tree']
        elif kind == 3123:
            return self.env['nostr.event.blob']
        else:
            return None

    def publish_event(self):
        self.ensure_one()
        relay_urls = self.env['ir.config_parameter'].sudo().get_param('integrated_ivcs.relay_urls', '').split(',')
        
        event_data = {
            'id': self.event_id,
            'kind': self.kind,
            'created_at': self.created_at,
            'tags': json.loads(self.tags),
            'content': self.content,
            'pubkey': self.public_key,
            'sig': self.signature,
        }

        for url in relay_urls:
            try:
                # Here you would typically use a Nostr client library to publish the event
                # For simplicity, we'll just log the action
                _logger.info(f"Publishing event {self.event_id} to relay: {url}")
                # Example: nostr_client.publish_event(url, event_data)
                self.published = True
            except Exception as e:
                _logger.error(f"Failed to publish event to {url}: {str(e)}")

    @api.model
    def create_git_event(self, repo_path, commit_hash):
        repo = git.Repo(repo_path)
        commit = repo.commit(commit_hash)
        
        commit_event = self.env['nostr.event.commit'].create({
            'id': commit_hash,  # Using commit hash as event ID
            'pubkey': self.env.user.nostr_public_key,
            'sig': 'placeholder',  # This should be properly signed
            'commit_hash': commit_hash,
            'message': commit.message,
            'author': f"{commit.author.name} <{commit.author.email}>",
            'timestamp': commit.committed_datetime.isoformat(),
            'content': json.dumps({
                'hash': commit_hash,
                'message': commit.message,
                'author': f"{commit.author.name} <{commit.author.email}>",
                'date': commit.committed_datetime.isoformat(),
            })
        })
        
        return commit_event

    @api.model
    def create_tree_event(self, repo_path, tree_hash):
        repo = git.Repo(repo_path)
        tree = repo.tree(tree_hash)
        
        content = json.dumps({
            "action": "tree",
            "hash": tree_hash,
            "items": [{"mode": item.mode, "type": item.type, "hash": item.hexsha, "path": item.path} for item in tree.traverse()],
        })
        
        event = Event(
            kind=3122,
            content=content,
            tags=[
                ["r", repo_path],
                ["h", tree_hash],
            ],
            public_key=self.env.user.nostr_public_key,
        )
        
        private_key = PrivateKey(bytes.fromhex(self.env.user.nostr_private_key))
        private_key.sign_event(event)
        
        return self.create_and_publish(event)

    @api.model
    def create_blob_event(self, repo_path, blob_hash):
        repo = git.Repo(repo_path)
        blob = repo.blob(blob_hash)
        
        content = json.dumps({
            "action": "blob",
            "hash": blob_hash,
            "size": blob.size,
            "data": blob.data_stream.read().decode('utf-8', errors='replace'),
        })
        
        event = Event(
            kind=3123,
            content=content,
            tags=[
                ["r", repo_path],
                ["h", blob_hash],
            ],
            public_key=self.env.user.nostr_public_key,
        )
        
        private_key = PrivateKey(bytes.fromhex(self.env.user.nostr_private_key))
        private_key.sign_event(event)
        
        return self.create_and_publish(event)

    @api.model
    def reconstruct_git_objects(self, repo_path):
        repo = git.Repo(repo_path)
        events = self.search([('tags', 'ilike', repo_path)])
        
        for event in events:
            content = json.loads(event.content)
            if event.kind == 3121:  # Commit
                self._reconstruct_commit(repo, content)
            elif event.kind == 3122:  # Tree
                self._reconstruct_tree(repo, content)
            elif event.kind == 3123:  # Blob
                self._reconstruct_blob(repo, content)

    def _reconstruct_commit(self, repo, content):
        commit_hash = content['hash']
        if commit_hash not in repo.objects:
            repo.create_commit(
                tree=repo.tree(content['tree_hash']),
                message=content['message'],
                author=git.Actor(content['author'], content['email']),
                committer=git.Actor(content['author'], content['email']),
                parent_commits=[repo.commit(p) for p in content['parent_hashes']],
                commit_timestamp=int(content['date']),
                ref=f'refs/heads/{content["branch"]}' if 'branch' in content else None
            )

    def _reconstruct_tree(self, repo, content):
        tree_hash = content['hash']
        if tree_hash not in repo.objects:
            tree_items = []
            for item in content['items']:
                if item['type'] == 'blob':
                    tree_items.append((item['mode'], 'blob', item['hash'], item['path']))
                elif item['type'] == 'tree':
                    tree_items.append((item['mode'], 'tree', item['hash'], item['path']))
            repo.create_tree(tree_items)

    def _reconstruct_blob(self, repo, content):
        blob_hash = content['hash']
        if blob_hash not in repo.objects:
            repo.create_blob(content['data'].encode('utf-8'))

    def sync_git_nostr(self, repo_path):
        repo = git.Repo(repo_path)
        for obj in repo.objects:
            if isinstance(obj, git.Commit):
                self.create_git_event(repo_path, obj.hexsha)
            elif isinstance(obj, git.Tree):
                self.create_tree_event(repo_path, obj.hexsha)
            elif isinstance(obj, git.Blob):
                self.create_blob_event(repo_path, obj.hexsha)

        self.reconstruct_git_objects(repo_path)
