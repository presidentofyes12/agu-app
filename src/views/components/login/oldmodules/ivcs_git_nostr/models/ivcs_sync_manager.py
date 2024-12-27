from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import git
import json

_logger = logging.getLogger(__name__)

class IVCSSyncManager(models.Model):
    _name = 'ivcs.sync.manager'
    _description = 'IVCS Sync Manager'

    name = fields.Char(string='Name', required=True)
    item_ids = fields.One2many('ivcs.item', 'sync_manager_id', string='IVCS Items')
    relay_urls = fields.Text(string='Relay URLs', help="Comma-separated list of Nostr relay URLs")
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)

    def sync_git_repository(self, repo_path):
        self.ensure_one()
        _logger.info(f"Starting sync for repository: {repo_path}")
        
        try:
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            
            # Fetch updates from remote
            origin.fetch()
            
            # Get current branch
            current_branch = repo.active_branch.name
            
            # Check if there are any local changes
            if repo.is_dirty() or repo.untracked_files:
                _logger.warning(f"Local changes detected in {repo_path}. Committing before sync.")
                repo.git.add(A=True)
                repo.index.commit("Automatic commit before sync")
            
            # Pull changes
            origin.pull(current_branch)
            
            # Push local changes
            origin.push(current_branch)
            
            self.last_sync_date = fields.Datetime.now()
            _logger.info(f"Sync completed for repository: {repo_path}")
            
            # Create and publish Nostr event for the sync
            self._create_sync_event(repo_path, current_branch)
            
            return True
        except git.GitCommandError as e:
            _logger.error(f"Git error during sync of {repo_path}: {str(e)}")
            raise UserError(_(f"Git error during sync: {str(e)}"))
        except Exception as e:
            _logger.error(f"Error during sync of {repo_path}: {str(e)}")
            raise UserError(_(f"Error during sync: {str(e)}"))

    def _create_sync_event(self, repo_path, branch):
        event_data = {
            'kind': 31337,  # Custom event kind for IVCS sync
            'content': json.dumps({
                'action': 'sync',
                'repo_path': repo_path,
                'branch': branch,
                'timestamp': fields.Datetime.now().isoformat(),
            }),
            'tags': [
                ['r', repo_path],
                ['b', branch],
            ],
        }
        
        self.env['nostr.event'].create_and_publish_event(event_data, self.relay_urls)

    def propagate_update(self, program):
        self.ensure_one()
        _logger.info(f"Propagating update for program: {program.name}")
        
        try:
            # Create a Nostr event for the program update
            event_data = {
                'kind': 31338,  # Custom event kind for program updates
                'content': json.dumps({
                    'action': 'update',
                    'program_id': program.id,
                    'program_name': program.name,
                    'content': program.content,
                    'version': program.version,
                    'timestamp': fields.Datetime.now().isoformat(),
                }),
                'tags': [
                    ['p', str(program.id)],
                    ['v', str(program.version)],
                ],
            }
            
            self.env['nostr.event'].create_and_publish_event(event_data, self.relay_urls)
            
            _logger.info(f"Update propagated for program: {program.name}")
            return True
        except Exception as e:
            _logger.error(f"Error propagating update for program {program.name}: {str(e)}")
            raise UserError(_(f"Error propagating update: {str(e)}"))

    @api.model
    def sync_all_repositories(self):
        sync_managers = self.search([])
        for manager in sync_managers:
            for item in manager.item_ids:
                try:
                    manager.sync_git_repository(item.repo_path)
                except Exception as e:
                    _logger.error(f"Error syncing repository for item {item.name}: {str(e)}")
        
        return True

    def action_manual_sync(self):
        self.ensure_one()
        try:
            for item in self.item_ids:
                self.sync_git_repository(item.repo_path)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Completed'),
                    'message': _('All repositories have been synchronized.'),
                    'type': 'success',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Failed'),
                    'message': str(e),
                    'type': 'danger',
                }
            }
