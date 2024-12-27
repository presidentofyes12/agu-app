# models/gitlab_repository.py

import logging
from odoo.exceptions import UserError
from odoo import _, api, fields, models
import gitlab
import requests
from .custom_error_handler import gitlab_nostr_error_handler

_logger = logging.getLogger(__name__)

class GitlabRepository(models.Model):
    _name = 'gitlab.repository'
    _description = 'GitLab Repository'

    name = fields.Char(string='Repository Name', required=True)
    gitlab_id = fields.Integer(string='GitLab Repository ID')
    url = fields.Char(string='GitLab URL')
    project_id = fields.Integer(string='GitLab Project ID')
    branch_ids = fields.One2many('gitlab.branch', 'repository_id', string='Branches')
    commit_ids = fields.One2many('gitlab.commit', 'repository_id', string='Commits')

    def action_test_publish_nostr_event(self):
        self.ensure_one()
        user = self.env.user
        if not user.nostr_private_key or not user.nostr_public_key:
            raise UserError(_("Nostr keys are not set for the current user. Please set them in user preferences."))
    
        public_key = user.nostr_public_key
        private_key = user.nostr_private_key
        relay_urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
        relay_urls = [url.strip() for url in relay_urls if url.strip()]
    
        if not relay_urls:
            raise UserError(_("No Nostr relay URLs configured. Please set them in the settings."))
    
        content = f"Test Nostr event from GitLab Repository: {self.name}"
        tags = [['r', self.url]]
    
        try:
            _logger.info(f"Attempting to publish test Nostr event for repository: {self.name}")
            _logger.info(f"Public key: {public_key}")
            _logger.info(f"Relay URLs: {relay_urls}")
            
            results = self.env['nostr.event'].publish_event_sync(
                content, public_key, private_key, relay_urls, kind=1, tags=tags
            )
            
            success_count = sum(1 for result in results if result['success'])
            
            if success_count > 0:
                message = f"Successfully published test Nostr event to {success_count} out of {len(relay_urls)} relays."
                message_type = 'success'
            else:
                message = "Failed to publish test Nostr event to any relay. Check the logs for detailed error messages."
                message_type = 'warning'
            
            # Detailed error reporting
            error_messages = []
            for result in results:
                if not result['success']:
                    error_messages.append(f"Relay {result['url']}: {result.get('error', 'Unknown error')}")
            
            if error_messages:
                message += "\n\nErrors:\n" + "\n".join(error_messages)
            
            _logger.info(message)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Test Nostr Event Publication"),
                    'message': message,
                    'type': message_type,
                    'sticky': True,
                }
            }
        except Exception as e:
            _logger.error(f"Error in action_test_publish_nostr_event: {str(e)}", exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
        
    def action_create_commit(self):
        return {
            'name': 'Create Commit',
            'type': 'ir.actions.act_window',
            'res_model': 'gitlab_nostr_bridge.create.commit.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    @gitlab_nostr_error_handler
    def sync_all_repositories(self):
        _logger.info("Starting synchronization of all GitLab repositories")
        repositories = self.search([])
        for repo in repositories:
            repo.sync_with_gitlab()
        _logger.info("Finished synchronization of all GitLab repositories")

    @gitlab_nostr_error_handler
    def sync_with_gitlab(self):
        self.ensure_one()
        _logger.info(f"Starting sync for GitLab repository: {self.name} (ID: {self.id})")
        
        gitlab_url = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_url')
        gitlab_token = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_private_token')

        if not gitlab_url or not gitlab_token:
            _logger.error("GitLab URL or Private Token not configured")
            raise UserError(_("GitLab URL or Private Token is not configured. Please check the settings."))

        try:
            gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token, timeout=30)
            gl.auth()
            _logger.info(f"Successfully authenticated with GitLab for repository: {self.name}")
            
            project = gl.projects.get(self.project_id)
            _logger.info(f"Retrieved GitLab project for repository: {self.name}")
            
            # Update repository details
            self.write({
                'gitlab_id': project.id,
                'url': project.web_url,
            })
            
            # Sync branches
            _logger.info(f"Starting branch sync for repository: {self.name}")
            for branch in project.branches.list():
                self.env['gitlab.branch'].create_or_update_from_gitlab(self.id, branch)
            _logger.info(f"Finished branch sync for repository: {self.name}")
            
            # Sync commits
            _logger.info(f"Starting commit sync for repository: {self.name}")
            for commit in project.commits.list():
                self.env['gitlab.commit'].create_or_update_from_gitlab(self.id, commit)
            _logger.info(f"Finished commit sync for repository: {self.name}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Sync Successful"),
                    'message': _("Repository synced successfully with GitLab."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except gitlab.exceptions.GitlabAuthenticationError:
            _logger.error(f"GitLab authentication failed for repository: {self.name}", exc_info=True)
            raise UserError(_("Failed to authenticate with GitLab. Please check your GitLab private token."))
        except gitlab.exceptions.GitlabGetError as e:
            _logger.error(f"Failed to retrieve GitLab project for repository: {self.name}", exc_info=True)
            raise UserError(_("Failed to retrieve GitLab project. Error: %s") % str(e))
        except Exception as e:
            _logger.error(f"Unexpected error during GitLab sync for repository: {self.name}", exc_info=True)
            raise UserError(_("An unexpected error occurred: %s") % str(e))

    @api.model
    @gitlab_nostr_error_handler
    def create(self, vals):
        _logger.info(f"Creating new GitLab repository: {vals.get('name')}")
        gitlab_url = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_url')
        gitlab_token = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_private_token')

        if not gitlab_url or not gitlab_token:
            _logger.error("GitLab URL or Private Token not configured")
            raise UserError(_("GitLab URL or Private Token is not configured. Please check the settings."))

        _logger.info(f"Attempting to connect to GitLab at {gitlab_url}")

        try:
            gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token, timeout=10)
            gl.auth()
            _logger.info("Successfully authenticated with GitLab")
            
            project = gl.projects.create({'name': vals['name']})
            _logger.info(f"Successfully created GitLab project: {project.name}")
            
            vals.update({
                'gitlab_id': project.id,
                'url': project.web_url,
                'project_id': project.id,
            })
            
            repo = super(GitlabRepository, self).create(vals)
            repo.sync_with_gitlab()
            return repo
        except gitlab.exceptions.GitlabAuthenticationError:
            _logger.error("GitLab authentication failed", exc_info=True)
            raise UserError(_("Failed to authenticate with GitLab. Please check your GitLab private token."))
        except gitlab.exceptions.GitlabCreateError as e:
            _logger.error(f"Failed to create GitLab project: {str(e)}", exc_info=True)
            raise UserError(_("Failed to create GitLab project. Error: %s") % str(e))
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to connect to GitLab: {str(e)}", exc_info=True)
            raise UserError(_("Failed to connect to GitLab. Please check the GitLab URL and your network connection."))
        except Exception as e:
            _logger.error(f"Unexpected error when connecting to GitLab: {str(e)}", exc_info=True)
            raise UserError(_("An unexpected error occurred: %s") % str(e))
