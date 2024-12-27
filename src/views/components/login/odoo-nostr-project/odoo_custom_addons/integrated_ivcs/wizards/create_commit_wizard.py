from odoo import models, fields, api

class CreateCommitWizard(models.TransientModel):
    _name = 'create.commit.wizard'
    _description = 'Create Commit Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    message = fields.Text(string='Commit Message', required=True)

    def action_create_commit(self):
        self.ensure_one()
        repo = self.env['git.repository'].search([('path', '=', self.item_id.repo_path)])
        commit_hash = repo.commit_changes(self.message)
        self.env['ivcs.commit'].create({
            'hash': commit_hash,
            'message': self.message,
            'author': self.env.user.name,
            'date': fields.Datetime.now(),
            'item_id': self.item_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}
