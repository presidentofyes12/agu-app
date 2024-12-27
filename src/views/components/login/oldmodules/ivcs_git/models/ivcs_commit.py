# File: odoo_custom_addons/ivcs_git/models/ivcs_commit.py

from odoo import models, fields, api

class IVCSCommit(models.Model):
    _name = 'ivcs.commit'
    _description = 'IVCS Commit'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True, ondelete='cascade')
    commit_hash = fields.Char('Commit Hash', required=True)
    message = fields.Text('Commit Message')
    branch = fields.Char('Branch', required=True)
    timestamp = fields.Datetime('Timestamp')
