from odoo import http
from odoo.http import request

class GitRepositoryController(http.Controller):
    @http.route('/git/repository/create', type='json', auth='user')
    def create_repository(self, name, path, description, maintainer_ids):
        repo_manager = request.env['git.repository.manager'].sudo()
        repo_id = repo_manager.create_repository(name, path, description, maintainer_ids)
        return {'success': True, 'repository_id': repo_id}

    @http.route('/git/repository/update', type='json', auth='user')
    def update_repository(self, repo_id, description=None, maintainer_ids=None):
        repo_manager = request.env['git.repository.manager'].sudo()
        updated_repo_id = repo_manager.update_repository(repo_id, description, maintainer_ids)
        return {'success': True, 'repository_id': updated_repo_id}

    @http.route('/git/repository/fork', type='json', auth='user')
    def fork_repository(self, original_repo_id, new_name):
        repo_manager = request.env['git.repository.manager'].sudo()
        forked_repo_id = repo_manager.fork_repository(original_repo_id, new_name, request.env.user.id)
        return {'success': True, 'repository_id': forked_repo_id}

    @http.route('/git/repository/list_maintainers', type='json', auth='user')
    def list_maintainers(self, repo_id):
        repo_manager = request.env['git.repository.manager'].sudo()
        maintainer_ids = repo_manager.list_maintainers(repo_id)
        return {'success': True, 'maintainer_ids': maintainer_ids}
