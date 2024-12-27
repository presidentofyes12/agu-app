from odoo import models, fields

class CreateCommitWizard(models.TransientModel):
    _name = 'create.commit.wizard'

    repository_id = fields.Many2one('git.repository', string='Repository', required=True)
    message = fields.Text(string='Commit Message', required=True)

    def action_create_commit(self):
        self.ensure_one()

        # Commit changes to the repository
        commit_hash = self.repository_id.commit_changes(self.message)

        # Create a record of the commit in Odoo
        self.env['git.commit'].create({
            'hash': commit_hash,
            'message': self.message,
            'author': self.env.user.name,
            'date': fields.Datetime.now(),
            'repository_id': self.repository_id.id,
        })

        return {'type': 'ir.actions.act_window_close'}
