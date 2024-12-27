from odoo import models, fields

class GitCommit(models.Model):
    _name = 'git.commit'
    _description = 'Git Commit'

    hash = fields.Char(string='Commit Hash', required=True)
    message = fields.Text(string='Commit Message', required=True)
    author = fields.Char(string='Author', required=True)
    date = fields.Datetime(string='Date', required=True)
    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
