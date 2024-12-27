# models/git_repository.py
from odoo import models, fields, api
import git
import json

class GitRepository(models.Model):
    _name = 'git.repository'
    _description = 'Git Repository'

    name = fields.Char(string='Name', required=True)
    path = fields.Char(string='Path', required=True)
    logs = fields.Text(string='Logs')

    def traverse_and_publish(self):
        self.ensure_one()
        logs = []
        try:
            git_repo = git.Repo(self.path)
            for commit in git_repo.iter_commits():
                nostr_event = self.env['nostr.event.object'].create({
                    'kind': 1,
                    'content': commit.message,
                    'tags': json.dumps([['commit', commit.hexsha]]),
                    'created_at': commit.committed_date,
                })
                nostr_event.action_publish()
                logs.append(f"Published commit {commit.hexsha}")

            self.write({'logs': '\n'.join(logs)})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'title': _("Git Repository Traversed"),
                'message': _("All commits published to Nostr network"),
            })
        except Exception as e:
            error_msg = f"Error traversing repository: {e}"
            logs.append(error_msg)
            self.write({'logs': '\n'.join(logs)})
            raise UserError(_(error_msg))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Git Repository"),
                'message': _("Repository traversed and commits published. Check logs for details."),
                'sticky': False,
                'type': 'success',
            }
        }
