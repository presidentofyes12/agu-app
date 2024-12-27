from odoo import models, fields, api
from dateutil import parser
from datetime import datetime, timezone

class GitlabBranch(models.Model):
    _name = 'gitlab.branch'
    _description = 'GitLab Branch'

    name = fields.Char(string='Branch Name', required=True)
    repository_id = fields.Many2one('gitlab.repository', string='Repository', required=True)
    last_commit_date = fields.Datetime(string='Last Commit Date')
    commit_ids = fields.Many2many('gitlab.commit', string='Commits')

    @api.model
    def create_or_update_from_gitlab(self, repository_id, gitlab_branch):
        existing_branch = self.search([('name', '=', gitlab_branch.name), ('repository_id', '=', repository_id)])
        last_commit_date = self._convert_to_naive_datetime(gitlab_branch.commit['committed_date']) if gitlab_branch.commit else False
        if existing_branch:
            return existing_branch.write({
                'last_commit_date': last_commit_date,
            })
        else:
            return self.create({
                'name': gitlab_branch.name,
                'repository_id': repository_id,
                'last_commit_date': last_commit_date,
            })

    def _convert_to_naive_datetime(self, date_string):
        dt = parser.parse(date_string)
        return dt.replace(tzinfo=None)
