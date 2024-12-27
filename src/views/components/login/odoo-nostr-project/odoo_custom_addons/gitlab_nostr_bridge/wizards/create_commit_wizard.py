# wizards/create_commit_wizard.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import gitlab
import base64
import logging
from bech32 import bech32_decode, convertbits
import json
import time

_logger = logging.getLogger(__name__)

class CreateCommitWizard(models.TransientModel):
    _name = 'gitlab_nostr_bridge.create.commit.wizard'
    _description = 'Create Commit Wizard'

    repository_id = fields.Many2one('gitlab.repository', string='Repository', required=True)
    branch_name = fields.Char(string='Branch Name', required=True, default='main')
    commit_message = fields.Text(string='Commit Message', required=True)
    file_path = fields.Char(string='File Path', required=True)
    file_content = fields.Text(string='File Content', required=True)
    file_upload = fields.Binary(string='Upload File')
    file_upload_filename = fields.Char(string='File Upload Filename')
    is_new_file = fields.Boolean(string='Is New File', compute='_compute_is_new_file', store=True)
    file_exists = fields.Boolean(string='File Exists', compute='_compute_file_exists', store=True)
    file_name = fields.Char(string='File Name')
    author_id = fields.Many2one('res.users', string='Author (Odoo User)', required=True)

    def _log_sanitized_data(self, data):
        """Sanitize sensitive data for logging."""
        sanitized = data.copy()
        if 'file_upload' in sanitized:
            sanitized['file_upload'] = '[BINARY DATA]'
        if 'file_content' in sanitized:
            sanitized['file_content'] = f"{sanitized['file_content'][:50]}..." if sanitized['file_content'] else ''
        return sanitized

    @api.model
    def create(self, vals):
        _logger.info(f"Creating commit wizard with data: {self._log_sanitized_data(vals)}")
        return super(CreateCommitWizard, self).create(vals)

    def write(self, vals):
        _logger.info(f"Updating commit wizard with data: {self._log_sanitized_data(vals)}")
        return super(CreateCommitWizard, self).write(vals)

    @api.depends('file_exists')
    def _compute_is_new_file(self):
        for record in self:
            record.is_new_file = not record.file_exists

    @api.depends('repository_id', 'branch_name', 'file_path')
    def _compute_file_exists(self):
        for record in self:
            record.file_exists = False
            if record.repository_id and record.branch_name and record.file_path:
                if not record.file_path.strip():
                    _logger.warning("File path is empty or only whitespace")
                    continue
                try:
                    _logger.info(f"Checking file existence: repo={record.repository_id.name}, branch={record.branch_name}, path={record.file_path}")
                    gl = record._get_gitlab_client()
                    project = gl.projects.get(record.repository_id.project_id)
                    try:
                        project.files.get(file_path=record.file_path, ref=record.branch_name)
                        record.file_exists = True
                        _logger.info(f"File exists: {record.file_path} in branch {record.branch_name}")
                    except gitlab.exceptions.GitlabGetError as e:
                        if e.response_code == 404:
                            record.file_exists = False
                            _logger.info(f"File does not exist: {record.file_path} in branch {record.branch_name}")
                        else:
                            _logger.error(f"GitLab API error: {str(e)}")
                            _logger.exception("Error checking file existence")
                except Exception as e:
                    _logger.error(f"Error in _compute_file_exists: {str(e)}")
                    _logger.exception("Error checking file existence")

    @api.model
    def default_get(self, fields_list):
        defaults = super(CreateCommitWizard, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id:
            repository = self.env['gitlab.repository'].browse(active_id)
            defaults['repository_id'] = repository.id
        return defaults

    @api.depends('repository_id')
    def _get_branch_selection(self):
        branches = []
        repository_id = self._context.get('default_repository_id')
        if self:
            repository = self.env['gitlab.repository'].browse(repository_id)
            if repository:
                try:
                    gl = self._get_gitlab_client()
                    project = gl.projects.get(repository.project_id)
                    branches = [(branch.name, branch.name) for branch in project.branches.list()]
                    _logger.info(f"Retrieved {len(branches)} branches for repository {repository.name}")
                except Exception as e:
                    _logger.error(f"Failed to fetch branches for repository {repository.name}: {str(e)}")
        if not branches:
            branches = [('main', 'main')]
        return branches

    @api.onchange('repository_id', 'branch_name', 'file_path')
    def _onchange_file_details(self):
        if self.repository_id and self.branch_name and self.file_path:
            if not self.file_path or '..' in self.file_path:
                return {'warning': {'title': _("Invalid File Path"), 'message': _("Please enter a valid file path.")}}
            
            try:
                gl = self._get_gitlab_client()
                project = gl.projects.get(self.repository_id.project_id)
                try:
                    file_content = project.files.get(file_path=self.file_path, ref=self.branch_name)
                    self.file_content = base64.b64decode(file_content.content).decode('utf-8')
                    self.is_new_file = False
                    _logger.info(f"Retrieved existing file content for {self.file_path}")
                except gitlab.exceptions.GitlabGetError as e:
                    if e.response_code == 404:
                        self.file_content = ''
                        self.is_new_file = True
                        _logger.info(f"File {self.file_path} does not exist, marked as new file")
                    else:
                        _logger.error(f"GitLab API error: {str(e)}")
                        return {'warning': {'title': _("GitLab Error"), 'message': str(e)}}
            except Exception as e:
                _logger.error(f"Error in _onchange_file_details: {str(e)}")
                return {'warning': {'title': _("Error"), 'message': str(e)}}

    @api.onchange('file_upload', 'file_upload_filename')
    def _onchange_file_upload(self):
        if self.file_upload:
            _logger.info(f"File upload detected. Filename: {self.file_upload_filename}")
            try:
                self.file_content = base64.b64decode(self.file_upload).decode('utf-8')
            except UnicodeDecodeError:
                self.file_content = "Binary file content"
            
            if self.file_upload_filename:
                self.file_name = self.file_upload_filename
                self.file_path = f"/{self.file_upload_filename}"
                self.commit_message = f"Add {self.file_upload_filename}"
                _logger.info(f"File path set to: {self.file_path}")
            else:
                _logger.warning("File uploaded but filename is missing")

            # Force UI update
            return {'domain': {'file_path': []}}

    @api.onchange('repository_id')
    def _onchange_repository_id(self):
        if self.repository_id:
            return {'domain': {'branch_name': []}, 'context': {'default_repository_id': self.repository_id.id}}

    def _get_gitlab_client(self):
        gitlab_url = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_url')
        gitlab_token = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_private_token')
        _logger.info(f"Attempting to create GitLab client with URL: {gitlab_url}")
        if not gitlab_url or not gitlab_token:
            raise UserError(_("GitLab URL or Private Token is not configured. Please check the settings."))
        try:
            return gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        except Exception as e:
            _logger.error(f"Failed to create GitLab client: {str(e)}")
            raise UserError(_("Failed to connect to GitLab. Please check your settings and network connection."))

    @api.constrains('file_path')
    def _check_file_path(self):
        for record in self:
            if not record.file_path or not record.file_path.strip():
                raise ValidationError(_("File path cannot be empty or only whitespace."))
            if '..' in record.file_path:
                raise ValidationError(_("Invalid file path. Please provide a valid path without '..'."))

    def action_create_commit(self):
        self.ensure_one()
        _logger.info(f"Starting commit creation process for repository: {self.repository_id.name}")
        try:
            gl = self._get_gitlab_client()
            _logger.info(f"GitLab client initialized for project ID: {self.repository_id.project_id}")
            
            project = gl.projects.get(self.repository_id.project_id)
            _logger.info(f"GitLab project retrieved: {project.name}")
            
            action = 'create' if self.is_new_file else 'update'
            _logger.info(f"Commit action: {action}, File path: {self.file_path}")
            
            commit_data = {
                'branch': self.branch_name,
                'commit_message': self.commit_message,
                'actions': [
                    {
                        'action': action,
                        'file_path': self.file_path,
                        'content': self.file_content,
                    }
                ]
            }
            _logger.info(f"Commit data prepared: {self._log_sanitized_data(commit_data)}")
            
            try:
                commit = project.commits.create(commit_data)
                _logger.info(f"Commit created successfully. Commit ID: {commit.id}")
            except gitlab.exceptions.GitlabCreateError as e:
                _logger.error(f"Failed to create commit: {str(e)}", exc_info=True)
                raise UserError(_("Failed to create commit: %s") % str(e))
            
            gitlab_commit = self.env['gitlab.commit'].create_or_update_from_gitlab(self.repository_id.id, commit)
            _logger.info(f"GitLab commit record created/updated in Odoo. ID: {gitlab_commit.id}")
            
            # Prepare Nostr event content
            nostr_content = json.dumps({
                "commit_hash": commit.id,
                "repository_path": self.repository_id.url,
                "commit_timestamp": int(time.time())
            })

            # Publish to Nostr
            try:
                self.env['nostr.publisher'].publish_event_for_module(
                    module_name='gitlab_nostr_bridge',
                    event_type='commit',
                    content=nostr_content,
                    tags=[['r', self.repository_id.url]]
                )
                _logger.info("Nostr event created and published for the commit")
            except Exception as e:
                _logger.error(f"Failed to create and publish Nostr event: {str(e)}", exc_info=True)
                # Continue with the commit process even if Nostr event fails
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Commit created successfully and published to Nostr"),
                    'type': 'success',
                }
            }
        except Exception as e:
            _logger.error(f"Unexpected error in action_create_commit: {str(e)}", exc_info=True)
            raise UserError(_("An unexpected error occurred: %s") % str(e))
