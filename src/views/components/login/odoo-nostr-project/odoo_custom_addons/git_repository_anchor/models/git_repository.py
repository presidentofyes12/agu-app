from odoo import models, fields, api, _
from odoo.exceptions import UserError
import git
import os
import logging

_logger = logging.getLogger(__name__)

class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Repository Name', required=True)
    path = fields.Char(string='Repository Path', required=True)
    description = fields.Text(string='Description', tracking=True)
    maintainer_ids = fields.Many2many('res.users', string='Maintainers')
    anchor_event_id = fields.Many2one('nostr.event', string='Anchor Event')
    #company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        repo = super(GitRepository, self).create(vals)
        repo._initialize_repository()
        return repo

    def _initialize_repository(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            git.Repo.init(self.path)
            readme_path = os.path.join(self.path, 'README.md')
            with open(readme_path, 'w') as f:
                f.write(f"# {self.name}\n\n{self.description or ''}")
            repo = git.Repo(self.path)
            repo.index.add(['README.md'])
            repo.index.commit("Initial commit")

    def _create_anchor_event(self):
        anchor = self.env['git.repository.anchor']
        event = anchor.create_anchor_event(self.path, self.maintainer_ids.mapped('nostr_public_key'))
        self.env['nostr.event'].create_and_publish(event)
        self.anchor_event_id = self.env['nostr.event'].search([('event_id', '=', event.id)], limit=1).id

    def update_maintainers(self):
        anchor = self.env['git.repository.anchor']
        event = anchor.update_anchor(self.path, self.maintainer_ids.mapped('nostr_public_key'))
        self.env['nostr.event'].create_and_publish(event)
        self.anchor_event_id = self.env['nostr.event'].search([('event_id', '=', event.id)], limit=1).id

    def fork_repository(self, new_name, new_path, new_maintainer_ids):
        anchor = self.env['git.repository.anchor']
        new_maintainers = self.env['res.users'].browse(new_maintainer_ids).mapped('nostr_public_key')
        event = anchor.fork_repository(self.path, new_path, new_maintainers)
        self.env['nostr.event'].create_and_publish(event)
        
        new_repo = self.create({
            'name': new_name,
            'path': new_path,
            'maintainer_ids': [(6, 0, new_maintainer_ids)],
        })
        new_repo.anchor_event_id = self.env['nostr.event'].search([('event_id', '=', event.id)], limit=1).id
        
        # Clone the repository
        git.Repo.clone_from(self.path, new_path)
        
        return new_repo

    def check_permission(self, user_id):
        user = self.env['res.users'].browse(user_id)
        anchor = self.env['git.repository.anchor']
        return anchor.check_permission(self.anchor_event_id, user.nostr_public_key)
