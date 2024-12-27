from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository'

    name = fields.Char(string='Repository Name', required=True)
    path = fields.Char(string='Repository Path', required=True)
    description = fields.Text(string='Description')
    maintainer_ids = fields.Many2many('res.users', string='Maintainers')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
    last_updated = fields.Datetime(string='Last Updated', default=fields.Datetime.now)
    branch_ids = fields.One2many('git.branch', 'repository_id', string='Branches')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(GitRepository, self).fields_get(allfields, attributes)
        _logger.info(f"Fields in GitRepository model: {res.keys()}")
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        _logger.info(f"Search_read called with fields: {fields}")
        return super(GitRepository, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    def read(self, fields=None, load='_classic_read'):
        _logger.info(f"Read called with fields: {fields}")
        return super(GitRepository, self).read(fields=fields, load=load)

    @api.model
    def create(self, vals):
        repo = super(GitRepository, self).create(vals)
        repo._create_default_branch()
        return repo

    def _create_default_branch(self):
        self.env['git.branch'].create({
            'name': 'main',
            'repository_id': self.id,
            'head': 'initial commit',
        })

class GitBranch(models.Model):
    _name = 'git.branch'
    _description = 'Git Branch'

    name = fields.Char(string='Branch Name', required=True)
    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
    head = fields.Char(string='Head Commit', required=True)

class GitEvent(models.Model):
    _name = 'git.event'
    _description = 'Git Event'

    event_type = fields.Selection([
        ('create_repository', 'Create Repository'),
        ('update_repository', 'Update Repository'),
        ('fork_repository', 'Fork Repository'),
        ('create_branch', 'Create Branch'),
        ('update_branch', 'Update Branch'),
        ('delete_branch', 'Delete Branch')
    ], string='Event Type')
    content = fields.Text(string='Event Content')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)

class GitRepositoryManager(models.Model):
    _name = 'git.repository.manager'
    _description = 'Git Repository Manager'

    @api.model
    def create_repository(self, name, path, description, maintainer_ids):
        anchor = self.env['git.repository.anchor']
        repo = anchor.create_repository(name, path, description, maintainer_ids)
        return repo.id

    @api.model
    def update_repository(self, repo_id, description=None, maintainer_ids=None):
        anchor = self.env['git.repository.anchor']
        repo = self.env['git.repository'].browse(repo_id)
        updated_repo = anchor.update_repository(repo, description, maintainer_ids)
        return updated_repo.id

    @api.model
    def fork_repository(self, original_repo_id, new_name, new_maintainer_id):
        anchor = self.env['git.repository.anchor']
        original_repo = self.env['git.repository'].browse(original_repo_id)
        forked_repo = anchor.fork_repository(original_repo, new_name, new_maintainer_id)
        return forked_repo.id

    @api.model
    def list_maintainers(self, repo_id):
        anchor = self.env['git.repository.anchor']
        repo = self.env['git.repository'].browse(repo_id)
        maintainers = anchor.list_maintainers(repo)
        return maintainers.ids
