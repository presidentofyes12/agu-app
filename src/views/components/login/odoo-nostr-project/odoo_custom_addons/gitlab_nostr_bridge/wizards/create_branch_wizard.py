# wizards/create_branch_wizard.py

from odoo import models, fields, api
import gitlab

class CreateBranchWizard(models.TransientModel):
    _name = 'gitlab_nostr_bridge.create.branch.wizard'
    _description = 'Create Branch Wizard'

    repository_id = fields.Many2one('gitlab.repository', string='Repository', required=True)
    branch_name = fields.Char(string='Branch Name', required=True)
    source_branch = fields.Char(string='Source Branch', default='master')

    def action_create_branch(self):
        self.ensure_one()
        gl = self._get_gitlab_client()
        project = gl.projects.get(self.repository_id.project_id)
        branch = project.branches.create({'branch': self.branch_name, 'ref': self.source_branch})
        
        self.env['gitlab.branch'].create_or_update_from_gitlab(self.repository_id.id, branch)
        
        self.env['nostr.event'].create_gitlab_event('branch', {
            'project_id': self.repository_id.project_id,
            'branch_name': self.branch_name,
            'action': 'create',
        })
        
        return {'type': 'ir.actions.act_window_close'}

    def _get_gitlab_client(self):
        gitlab_url = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_url')
        gitlab_token = self.env['ir.config_parameter'].sudo().get_param('gitlab_nostr_bridge.gitlab_private_token')
        if not gitlab_url or not gitlab_token:
            raise UserError(_("GitLab URL or Private Token is not configured. Please check the settings."))
        try:
            return gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        except Exception as e:
            _logger.error(f"Failed to create GitLab client: {str(e)}")
            raise UserError(_("Failed to connect to GitLab. Please check your settings and network connection."))
