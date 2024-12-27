from odoo import models, fields, api
from .repository_anchor import log_execution_time
from git import Repo, GitCommandError
import json
from nostr.event import Event
from nostr.key import PrivateKey
import logging

_logger = logging.getLogger(__name__)

class BranchManager(models.AbstractModel):
    _name = 'ivcs.branch.manager'
    _description = 'IVCS Branch Manager'

    name = fields.Char(string='Name', required=True)
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)

    @api.model
    @log_execution_time
    def create_branch(self, repository_id, name, head):
        repo = self.env['git.repository'].browse(repository_id)
        branch = self.env['git.branch'].create({
            'name': name,
            'repository_id': repository_id,
            'head': head,
        })
        self._create_event('create_branch', branch)
        return branch.id

    @api.model
    @log_execution_time
    def update_branch(self, branch_id, new_head):
        branch = self.env['git.branch'].browse(branch_id)
        branch.write({'head': new_head})
        self._create_event('update_branch', branch)
        return branch.id

    @api.model
    @log_execution_time
    def delete_branch(self, branch_id):
        branch = self.env['git.branch'].browse(branch_id)
        self._create_event('delete_branch', branch)
        branch.unlink()
        return True

    @api.model
    def _create_event(self, event_type, branch):
        self.env['git.event'].create({
            'event_type': event_type,
            'content': f"{event_type}: {branch.name} in {branch.repository_id.name}",
        })
