# File: ivcs_item.py

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
import git
import os
import logging
import uuid
import json
from datetime import datetime
from difflib import unified_diff

_logger = logging.getLogger(__name__)

class IVCSItem(models.Model):
    _name = 'ivcs.item'
    _description = 'IVCS Item'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    current_version_id = fields.Many2one('ivcs.version', string='Current Version', ondelete='restrict')
    version_ids = fields.One2many('ivcs.version', 'item_id', string='Versions')
    repo_path = fields.Char('Repository Path', compute='_compute_repo_path')
    current_branch = fields.Char('Current Branch', default='main')
    commit_ids = fields.One2many('ivcs.commit', 'item_id', string='Commits')
    sync_manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    branch_manager_id = fields.Many2one('ivcs.branch.manager', string='Branch Manager')
    metadata_ids = fields.One2many('ivcs.metadata', 'item_id', string='Metadata')
    git_host = fields.Selection([
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('bitbucket', 'Bitbucket'),
        ('odoo', 'Odoo Instance'),
        ('other', 'Other')
    ], string='Git Hosting Service', default='other', required=True)
    git_token = fields.Char('Git Access Token', help="Personal access token for the Git hosting service")
    odoo_instance_url = fields.Char('Odoo Instance URL', help="URL of the Odoo instance for synchronization")
    odoo_database = fields.Char('Odoo Database', help="Database name of the Odoo instance")

    @api.depends('version_ids')
    def _compute_current_version(self):
        for item in self:
            valid_versions = item.version_ids.filtered(lambda v: v.exists())
            if not valid_versions:
                item._create_initial_version()
            else:
                item.current_version_id = item.current_version_id if item.current_version_id in valid_versions else valid_versions[0]

    @api.depends('name')
    def _compute_repo_path(self):
        for item in self:
            item.repo_path = f"/opt/ivcs_repos/item_{item.id}"

    def _default_version(self):
        return None

    @api.constrains('current_version_id')
    def _check_current_version(self):
        for record in self:
            if not record.current_version_id:
                raise ValidationError(_("A version must be associated with an IVCS item."))

    @api.onchange('current_version_id')
    def _onchange_current_version_id(self):
        if not self.current_version_id:
            self._create_initial_version()
        elif self.current_version_id.item_id != self:
            self.current_version_id = None
            self._create_initial_version()

    def _initialize_repository(self):
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            repo = git.Repo.init(self.repo_path)
            readme_path = os.path.join(self.repo_path, 'README.md')
            with open(readme_path, 'w') as f:
                f.write(f"# {self.name}\n\n{self.description}")
            repo.index.add(['README.md'])
            repo.index.commit("Initial commit")
            if not self.current_version_id:
                _logger.warning(f"No current version set for item {self.name}. Creating default version.")
                self._create_initial_version()
            self._create_commit("Initial commit")

    def _create_commit(self, message):
        current_version = self._get_current_version()
        commit = self.env['ivcs.commit'].create({
            'item_id': self.id,
            'message': message,
            'branch': self.current_branch,
            'commit_hash': self._get_latest_commit_hash(),
            'version_id': current_version.id,
        })
        return commit

    def set_as_current_version(self):
        self.ensure_one()
        self.item_id.current_version_id = self.id
    
    def _get_latest_commit_hash(self):
        try:
            repo = git.Repo(self.repo_path)
            return repo.head.commit.hexsha
        except Exception as e:
            _logger.error(f"Failed to get latest commit hash: {str(e)}")
            return None

    def create_branch(self, branch_name):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        current_branch = repo.active_branch.name
        if branch_name not in repo.heads:
            repo.create_head(branch_name)
            self.current_branch = branch_name
            repo.git.checkout(branch_name)
            self._create_git_event('branch', branch_name=branch_name)
            if self.branch_manager_id:
                self.branch_manager_id.create_branch(branch_name)
            return self._return_success('Branch Created', f'Branch {branch_name} has been created and checked out.')
        else:
            return self._return_warning('Branch Exists', f'Branch {branch_name} already exists.')

    def switch_branch(self, branch_name):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        if branch_name in repo.heads:
            repo.git.checkout(branch_name)
            self.current_branch = branch_name
            return self._return_success('Branch Switched', f'Switched to branch: {branch_name}')
        else:
            return self._return_warning('Branch Not Found', f'Branch {branch_name} does not exist.')

    def merge_branches(self, source_branch, target_branch):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        if source_branch not in repo.heads or target_branch not in repo.heads:
            return self._return_error('Branch Not Found', 'One or both branches do not exist.')

        current_branch = repo.active_branch.name
        repo.git.checkout(target_branch)
        try:
            repo.git.merge(source_branch)
            merge_commit = self._create_commit(f"Merge {source_branch} into {target_branch}")
            self._create_git_event('merge', source_branch=source_branch, target_branch=target_branch)
            return self._return_success('Branches Merged', f'Branch {source_branch} has been merged into {target_branch}.')
        except git.GitCommandError as e:
            if 'CONFLICT' in str(e):
                return self._return_warning('Merge Conflict', f'There are conflicts merging {source_branch} into {target_branch}. Please resolve conflicts manually.')
            else:
                return self._return_error('Merge Failed', str(e))
        finally:
            repo.git.checkout(current_branch)

    def rebase_branch(self, branch_name, onto_branch):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        if branch_name not in repo.heads or onto_branch not in repo.heads:
            return self._return_error('Branch Not Found', 'One or both branches do not exist.')

        current_branch = repo.active_branch.name
        try:
            repo.git.checkout(branch_name)
            repo.git.rebase(onto_branch)
            self._create_commit(f"Rebased {branch_name} onto {onto_branch}")
            return self._return_success('Rebase Completed', f'Successfully rebased {branch_name} onto {onto_branch}.')
        except git.GitCommandError as e:
            if 'CONFLICT' in str(e):
                return self._return_warning('Rebase Conflict', f'There are conflicts rebasing {branch_name} onto {onto_branch}. Please resolve conflicts manually.')
            else:
                return self._return_error('Rebase Failed', str(e))
        finally:
            repo.git.checkout(current_branch)

    def generate_diff(self, file_path, old_commit, new_commit):
        self.ensure_one()
        
        _logger.debug(f"Generating diff for file: {file_path}, old_commit: {old_commit}, new_commit: {new_commit}")
        
        if not old_commit or not new_commit:
            raise UserError(_("Invalid commit hashes provided for generating diff."))
        
        try:
            repo = git.Repo(self.repo_path)
            old_content = repo.git.show(f'{old_commit}:{file_path}')
            new_content = repo.git.show(f'{new_commit}:{file_path}')
            diff = list(unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f'a/{file_path}',
                tofile=f'b/{file_path}'
            ))
            return ''.join(diff)
        except git.GitCommandError as e:
            _logger.error(f"Failed to generate diff: {str(e)}")
            raise UserError(_("Failed to generate diff: %s") % str(e))

    def handle_merge_conflict(self, file_path):
        _logger.debug(f"Handling merge conflict for file: {file_path}")
        
        try:
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                content = f.read()
            return content
        except Exception as e:
            _logger.error(f"Failed to read conflicted file: {str(e)}")
            raise UserError(_("Failed to read conflicted file: %s") % str(e))

    def _get_current_version(self):
        self.ensure_one()
        if not self.current_version_id:
            self._create_initial_version()
        return self.current_version_id

    def action_create_file(self):
        # Debugging log to check action trigger
        _logger.debug("Action create file triggered.")
       
        return {
            'name': _('Create File'),
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.create.file.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_item_id': self.id},
        }

    def _create_git_event(self, event_type, **kwargs):
        nostr_event_manager=self.env['nostr.event.manager']
        if event_type=='commit':
            event=nostr_event_manager.create_git_event(self.repo_path, kwargs.get(
                'commit_hash'))
        elif event_type=='branch':
            event=nostr_event_manager.create_branch_event(
                self.repo_path,
                kwargs.get(
                    'branch_name'))
        elif event_type=='merge':
            event=nostr_event_manager.create_merge_event(
                self.repo_path,
                kwargs.get(
                    'source_branch'),
                kwargs.get(
                    'target_branch'))
        elif event_type=='tag':
            event=nostr_event_manager.create_tag_event(
                self.repo_path,
                kwargs.get(
                    'tag_name'),
                kwargs.get(
                    'tag_message'))
        else :
            raise UserError(_("Unsupported git event type"))
        nostr_event_manager.publish_event(event)

    def create_file(self, filename, content):
        _logger.info(f"Creating file: {filename}")
        _logger.debug(f"Filename type: {type(filename)}, Content type: {type(content)}")
        
        if not filename or not content:
            raise UserError(_("Filename and content must be provided."))

        try:
            file_path = os.path.join(self.repo_path, filename)
            with open(file_path, 'w') as f:
                f.write(content)

            repo = git.Repo(self.repo_path)
            repo.index.add([filename])
            commit = repo.index.commit(f"Add new file: {filename}")

            _logger.info(f"File created. Commit hash: {commit.hexsha}")

            self._create_git_event('commit', commit_hash=str(commit.hexsha))
            
            result = self.sync_repository()

            return self._return_success('File Created', f'File {filename} has been created and committed.')
        except Exception as e:
            _logger.error(f"Failed to create file: {str(e)}")
            raise UserError(_("Failed to create file: %s") % str(e))

    @api.model
    def create(self, vals):
        item = super(IVCSItem, self).create(vals)
        # Create initial version after the item is created
        version = self.env['ivcs.version'].create({
            'name': 'v1.0',
            'description': 'Initial version',
            'item_id': item.id,
        })
        item.current_version_id = version.id
        return item

    def unlink(self):
        for record in self:
            if record.version_ids:
                raise ValidationError(_("Cannot delete an IVCS item with existing versions. Please archive it instead."))
        return super(IVCSItem, self).unlink()
    
    def ensure_version(self):
        self.ensure_one()
        if not self.current_version_id:
            version = self.env['ivcs.version'].create({
                'name': 'v1.0',
                'description': 'Initial version',
                'item_id': self.id,
            })
            self.current_version_id = version.id

    def verify_remote_url(self):
        _logger.debug("Verifying remote URL.")
        
        try:
            repo = git.Repo(self.repo_path)
            remote_url = repo.remotes.origin.url

            from urllib.parse import urlparse, urlunparse
            parsed_url = urlparse(remote_url)
            clean_url = urlunparse(parsed_url._replace(netloc=parsed_url.netloc.split('@')[-1]))

            repo.remotes.origin.set_url(clean_url)

            _logger.info(f"Verified remote URL: {clean_url}")
            return self._return_success('Remote URL Verified', 'The remote URL has been verified and updated if necessary.')
        except Exception as e:
            _logger.error(f"Failed to verify remote URL: {str(e)}")
            raise UserError(_("Failed to verify remote URL: %s") % str(e))

    def _create_initial_version(self):
        self.ensure_one()
        if not self.current_version_id or not self.current_version_id.exists():
            version = self.env['ivcs.version'].create({
                'item_id': self.id,
                'name': 'v1.0',
                'description': 'Initial version',
            })
            self.current_version_id = version

    def setup_git_auth(self):
        git_token = self.git_token or self.env['ir.config_parameter'].sudo().get_param('ivcs_git.github_token')
        if not git_token:
            raise UserError(_("Git token not configured. Please set it in the settings or on the IVCS item."))
        
        repo = git.Repo(self.repo_path)
        with repo.config_writer() as git_config:
            git_config.set_value('user', 'name', 'Odoo IVCS')
            git_config.set_value('user', 'email', 'odoo@example.com')
        
        remote_url = repo.remotes.origin.url
        if not remote_url.startswith('https://'):
            raise UserError(_("Remote URL is not using HTTPS. Please update the remote URL."))
        
        # Parse the existing URL
        from urllib.parse import urlparse, urlunparse
        parsed_url = urlparse(remote_url)
        
        # Reconstruct the URL with the token
        new_netloc = f"{git_token}:x-oauth-basic@{parsed_url.netloc}"
        new_url = urlunparse(parsed_url._replace(netloc=new_netloc, scheme='https'))
        
        # Set the new URL for the origin remote
        repo.remotes.origin.set_url(new_url)
        
        # Set the credential helper to cache the token
        with repo.config_writer() as git_config:
            git_config.set_value('credential', 'helper', 'cache --timeout=3600')
        
        # Log the URL (without the token) for debugging
        _logger.info(f"Updated remote URL: https://{parsed_url.netloc}{parsed_url.path}")
    
    @api.model
    def _sync_repositories(self):
        items = self.search([])
        for item in items:
            repo = git.Repo(item.repo_path)
            try:
                repo.remotes.origin.pull()
                _logger.info(f"Successfully synced repository for item {item.name}")
            except Exception as e:
                _logger.error(f"Failed to sync repository for item {item.name}: {str(e)}")

    def sync_repository(self):
        self.ensure_one()
        if not self.current_version_id:
            _logger.warning(f"No current version set for item {self.name}. Setting default version before sync.")
            self._create_initial_version()

        try:
            self.verify_remote_url()
            self.setup_git_auth()
            
            repo = git.Repo(self.repo_path)
            if not repo.remotes:
                return self._return_warning('No Remote Repository', 'This repository does not have a remote configured. Please add a remote repository first.')
            
            origin = repo.remotes.origin
            if not origin.exists():
                return self._return_warning('Remote Not Found', 'The remote "origin" does not exist. Please configure the remote repository.')
            
            origin.fetch()
            
            current_branch = str(repo.active_branch)
            
            remote_branch = f'origin/{current_branch}'
            if remote_branch not in [str(ref) for ref in repo.references]:
                origin.push(current_branch)
                result = self._return_success('Branch Created', f'The branch "{current_branch}" has been created on the remote repository.')
            else:
                if repo.is_dirty() or repo.untracked_files:
                    repo.git.add(A=True)
                    repo.index.commit("Local changes before sync")
                
                origin.pull(current_branch)
                origin.push(current_branch)
                
                result = self._return_success('Repository Synced', 'The repository has been successfully synced.')
            
            self._create_git_event('commit', commit_hash=str(repo.head.commit.hexsha))
            
            if self.sync_manager_id:
                self.sync_manager_id.sync_git_repository(self.repo_path)
            
            if self.branch_manager_id:
                branches = self.branch_manager_id.list_branches()
                for branch in branches:
                    self.branch_manager_id.update_branch(branch)
            
            self.sync_with_decentralized_manager()
            
            return result
        except git.GitCommandError as e:
            _logger.error(f"Git command error: {str(e)}")
            return self._return_error('Sync Failed', f'Git command error: {str(e)}')
        except ValueError as e:
            _logger.error(f"Value error: {str(e)}")
            return self._return_error('Sync Failed', f'Value error: {str(e)}')
        except Exception as e:
            _logger.error(f"Error syncing repository: {str(e)}")
            return self._return_error('Sync Failed', f'An unexpected error occurred: {str(e)}')

    def sync_with_decentralized_manager(self):
        if not self.sync_manager_id:
            return

        repo = git.Repo(self.repo_path)
        for commit in repo.iter_commits():
            program = self.env['decentralized.sync.program'].search([
                ('manager_id', '=', self.sync_manager_id.id),
                ('content', '=', commit.message)
            ], limit=1)

            if not program:
                program = self.env['decentralized.sync.program'].create({
                    'manager_id': self.sync_manager_id.id,
                    'creator_id': self.env['decentralized.sync.creator'].search([], limit=1).id,
                    'content': commit.message,
                    'version': 1,
                    'size': 0.5  # Arbitrary size
                })

            self.sync_manager_id.propagate_update(program)

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

    def _return_error(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': _(message),
                'type': 'danger',
            }
        }

    def action_open_create_branch_wizard(self):
        self.ensure_one()
        return {
            'name': _('Create Branch'),
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.create.branch.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_item_id': self.id},
        }

    def add_remote(self, remote_url, remote_name='origin'):
        self.ensure_one()
        try:
            repo = git.Repo(self.repo_path)
            if remote_name in repo.remotes:
                repo.delete_remote(remote_name)
            repo.create_remote(remote_name, remote_url)
            return self._return_success('Remote Added', 'Remote repository has been added successfully.')
        except Exception as e:
            return self._return_error('Failed to Add Remote', f'An error occurred while adding the remote: {str(e)}')

    def action_open_add_remote_wizard(self):
        self.ensure_one()
        return {
            'name': _('Add Remote Repository'),
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.add.remote.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_item_id': self.id},
        }

    def action_reconstruct_branches(self):
        self.ensure_one()
        if self.branch_manager_id:
            self.branch_manager_id.reconstruct_branches_from_events()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Branches Reconstructed',
                'message': 'Branches have been reconstructed from Nostr events.',
                'type': 'success',
            }
        }

    def create_tag(self, tag_name, tag_message):
        self.ensure_one()
        repo = git.Repo(self.repo_path)
        repo.create_tag(tag_name, message=tag_message)
        self._create_git_event('tag', tag_name=tag_name, tag_message=tag_message)
        return self._return_success('Tag Created', f'Tag {tag_name} has been created.')

    @api.model
    def action_sync_with_odoo(self):
        for record in self:
            record._sync_with_odoo_instance()

    def _sync_with_odoo_instance(self):
        self.ensure_one()
        try:
            _logger.info(f"Syncing IVCS item {self.name} with Odoo instance: {self.odoo_instance_url}")
            
            # Placeholder for sync logic
            self.write({'description': f"Synced with Odoo at {fields.Datetime.now()}"})
            
            return self._return_success('Sync Completed', 'Successfully synced with Odoo.')
        except Exception as e:
            _logger.error(f"Error syncing with Odoo: {str(e)}")
            return self._return_error('Sync Failed', f'An error occurred during Odoo synchronization: {str(e)}')
