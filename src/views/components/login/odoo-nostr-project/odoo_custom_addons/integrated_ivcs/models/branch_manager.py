from odoo import models, fields, api
from git import Repo, GitCommandError
import json
from nostr.event import Event
from nostr.key import PrivateKey
import logging

_logger = logging.getLogger(__name__)

class BranchManager(models.Model):
    _name = 'ivcs.branch.manager'
    _description = 'IVCS Branch Manager'

    name = fields.Char(string='Name', required=True)
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)

    def create_branch(self, branch_name):
        self.ensure_one()
        repo = Repo(self.item_id.repo_path)
        if branch_name not in repo.heads:
            repo.create_head(branch_name)
            self._create_branch_event(branch_name, 'create')
            return True
        return False

    def delete_branch(self, branch_name):
        self.ensure_one()
        repo = Repo(self.item_id.repo_path)
        if branch_name in repo.heads:
            repo.delete_head(branch_name, force=True)
            self._create_branch_event(branch_name, 'delete')
            return True
        return False

    def update_branch(self, branch_name, new_commit):
        self.ensure_one()
        repo = Repo(self.item_id.repo_path)
        if branch_name in repo.heads:
            branch = repo.heads[branch_name]
            branch.set_commit(new_commit)
            self._create_branch_event(branch_name, 'update', new_commit)
            return True
        return False

    def merge_branches(self, source_branch, target_branch):
        self.ensure_one()
        repo = Repo(self.item_id.repo_path)
        if source_branch in repo.heads and target_branch in repo.heads:
            try:
                repo.git.checkout(target_branch)
                repo.git.merge(source_branch)
                self._create_branch_event(target_branch, 'merge', source_branch)
                return True
            except GitCommandError as e:
                _logger.error(f"Merge conflict: {str(e)}")
                repo.git.merge('--abort')
                return False
        return False

    def _create_branch_event(self, branch_name, action, additional_info=None):
        if not self.item_id.nostr_private_key:
            _logger.warning(f"No Nostr private key for item {self.item_id.name}")
            return

        private_key = PrivateKey(bytes.fromhex(self.item_id.nostr_private_key))
        content = {
            "action": action,
            "branch_name": branch_name,
            "repo_name": self.item_id.name
        }
        if additional_info:
            content["additional_info"] = additional_info

        event = Event(
            kind=31227,
            content=json.dumps(content),
            tags=[['r', self.item_id.repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)
        
        self.env['nostr.event'].create_and_publish(event)

    def list_branches(self):
        self.ensure_one()
        repo = Repo(self.item_id.repo_path)
        return [head.name for head in repo.heads]

    def reconstruct_branches_from_events(self):
        self.ensure_one()
        events = self.env['nostr.event'].search([
            ('kind', '=', 31227),
            ('tags', 'ilike', self.item_id.repo_path)
        ], order='created_at asc')

        branches = {}
        for event in events:
            content = json.loads(event.content)
            action = content.get('action')
            branch_name = content.get('branch_name')

            if action == 'create':
                branches[branch_name] = {'created_at': event.created_at}
            elif action == 'delete':
                branches.pop(branch_name, None)
            elif action == 'update':
                if branch_name in branches:
                    branches[branch_name]['last_updated'] = event.created_at
            elif action == 'merge':
                if branch_name in branches:
                    branches[branch_name]['last_merged'] = event.created_at
                    branches[branch_name]['merged_from'] = content.get('additional_info')

        return branches
