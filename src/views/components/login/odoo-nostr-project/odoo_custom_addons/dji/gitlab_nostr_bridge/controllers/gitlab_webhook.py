# In a new file, e.g., controllers/gitlab_webhook.py
from odoo import http
from odoo.http import request

class GitLabWebhookController(http.Controller):
    @http.route('/gitlab/webhook', type='json', auth='public', methods=['POST'])
    def gitlab_webhook(self, **post):
        if request.httprequest.headers.get('X-Gitlab-Token') != request.env['ir.config_parameter'].sudo().get_param('gitlab_webhook_token'):
            return 'Invalid token'
        
        data = request.jsonrequest
        if data.get('object_kind') == 'push':
            for commit in data.get('commits', []):
                request.env['gitlab.commit'].sudo().create_or_update_from_webhook(commit, data)
        return 'OK'
