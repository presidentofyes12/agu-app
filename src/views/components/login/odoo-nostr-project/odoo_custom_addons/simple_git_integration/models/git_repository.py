from odoo import models, fields, api
import git
import os

class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository'

    name = fields.Char(string='Repository Name', required=True)
    path = fields.Char(string='Repository Path', required=True)

    @api.model
    def create(self, vals):
        repo = super(GitRepository, self).create(vals)
        if not os.path.exists(repo.path):
            os.makedirs(repo.path)
            git.Repo.init(repo.path)
        return repo

    def commit_changes(self, message):
        repo = git.Repo(self.path)
        repo.git.add(A=True)
        commit = repo.index.commit(message)
        return commit.hexsha
