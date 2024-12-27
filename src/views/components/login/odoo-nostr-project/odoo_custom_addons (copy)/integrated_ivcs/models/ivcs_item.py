from odoo import models, fields, api, _
from odoo.exceptions import UserError
import git
import json
from nostr.event import Event
from nostr.key import PrivateKey
import os
import logging

_logger = logging.getLogger(__name__)

class IVCSItem(models.Model):
    _name = 'ivcs.item'
    _description = 'IVCS Item'

    name = fields.Char(string='Name', required=True)
    description = fields.Text('Description')
    current_version_id = fields.Many2one('ivcs.version', string='Current Version', compute='_compute_current_version', store=True)
    version_ids = fields.One2many('ivcs.version', 'item_id', string='Versions')
    repo_path = fields.Char('Repository Path', compute='_compute_repo_path', store=True)
    current_branch = fields.Char('Current Branch', default='main')
    commit_ids = fields.One2many('ivcs.commit', 'item_id', string='Commits')
    nostr_private_key = fields.Char(string="Nostr Private Key")
    branch_manager_id = fields.Many2one('ivcs.branch.manager', string='Branch Manager')

    @api.depends('name')
    def _compute_repo_path(self):
        for item in self:
            item.repo_path = f"/opt/ivcs_repos/item_{item.id}"

    @api.depends('version_ids')
    def _compute_current_version(self):
        for item in self:
            if item.version_ids:
                item.current_version_id = item.version_ids.sorted(lambda v: v.create_date, reverse=True)[0]
            else:
                item.current_version_id = False

    @api.model
    def create(self, vals):
        if 'nostr_private_key' in vals and vals['nostr_private_key']:
            try:
                # Validate and format the private key
                private_key = PrivateKey.from_nsec(vals['nostr_private_key'])
                vals['nostr_private_key'] = private_key.hex()  # Store the private key as a hex string
            except Exception as e:
                raise UserError(_("Invalid Nostr private key: %s") % str(e))
        return super(IVCSItem, self).create(vals)

    def write(self, vals):
        if 'nostr_private_key' in vals and vals['nostr_private_key']:
            try:
                # Validate and format the private key
                private_key = PrivateKey.from_nsec(vals['nostr_private_key'])
                vals['nostr_private_key'] = private_key.hex()  # Store the private key as a hex string
            except Exception as e:
                raise UserError(_("Invalid Nostr private key: %s") % str(e))
        return super(IVCSItem, self).write(vals)

    def _initialize_repository(self):
        self.ensure_one()
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            repo = git.Repo.init(self.repo_path)
            readme_path = os.path.join(self.repo_path, 'README.md')
            with open(readme_path, 'w') as f:
                f.write(f"# {self.name}\n\n{self.description}")
            repo.index.add(['README.md'])
            commit = repo.index.commit("Initial commit")
            self._create_initial_version(commit.hexsha)
            self._create_nostr_repo_event()

    def _create_initial_version(self, commit_hash):
        version = self.env['ivcs.version'].create({
            'name': 'v1.0',
            'description': 'Initial version',
            'item_id': self.id,
        })
        self.env['ivcs.commit'].create({
            'hash': commit_hash,
            'message': "Initial commit",
            'item_id': self.id,
            'version_id': version.id,
        })

    def _create_nostr_repo_event(self):
        if not self.nostr_private_key:
            raise UserError(_("Nostr private key is not set for this item."))
    
        private_key = PrivateKey(bytes.fromhex(self.nostr_private_key))
        event = Event(
            kind=31228,
            content=json.dumps({
                "action": "create_repository",
                "repo_name": self.name,
                "description": self.description
            }),
            tags=[['r', self.repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)
        
        self.env['nostr.event'].create_and_publish(event)

    def create_branch(self, branch_name):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        if not self.branch_manager_id:
            self.branch_manager_id = self.env['ivcs.branch.manager'].create({
                'name': f"Branch Manager for {self.name}",
                'item_id': self.id,
            })
        if branch_name not in repo.heads:
            repo.create_head(branch_name)
            self.current_branch = branch_name
            self._create_nostr_branch_event(branch_name)
            if self.branch_manager_id:
                self.branch_manager_id.create_branch(branch_name)
            return self._return_success('Branch Created', f'Branch {branch_name} has been created.')
        else:
            return self._return_warning('Branch Exists', f'Branch {branch_name} already exists.')

    def _create_nostr_branch_event(self, branch_name):
        if not self.nostr_private_key:
            raise UserError(_("Nostr private key is not set for this item."))
        
        private_key = PrivateKey(bytes.fromhex(self.nostr_private_key))
        event = Event(
            kind=31227,
            content=json.dumps({
                "action": "create_branch",
                "branch_name": branch_name,
                "repo_name": self.name
            }),
            tags=[['r', self.repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)
        
        self.env['nostr.event'].create_and_publish(event)

    def _return_success(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': _(message),
                'type': 'success',
            }
        }

    def _return_warning(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': _(message),
                'type': 'warning',
            }
        }

    def delete_branch(self, branch_name):
        self.ensure_one()
        if self.branch_manager_id.delete_branch(branch_name):
            return self._return_success('Branch Deleted', f'Branch {branch_name} has been deleted.')
        else:
            return self._return_warning('Branch Not Found', f'Branch {branch_name} does not exist.')

    def merge_branches(self, source_branch, target_branch):
        self.ensure_one()
        if self.branch_manager_id.merge_branches(source_branch, target_branch):
            return self._return_success('Branches Merged', f'Branch {source_branch} has been merged into {target_branch}.')
        else:
            return self._return_warning('Merge Failed', f'Failed to merge {source_branch} into {target_branch}.')

    def reconstruct_branches(self):
        self.ensure_one()
        branches = self.branch_manager_id.reconstruct_branches_from_events()
        return self._return_success('Branches Reconstructed', f'Reconstructed {len(branches)} branches from Nostr events.')

    # Add other methods as needed (e.g., commit, push, pull, etc.)
