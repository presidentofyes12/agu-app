from odoo import models, fields, api

class UpdateRelativeWizard(models.TransientModel):
    _name = 'update.relative.wizard'
    _description = 'Update Relative Wizard'

    relative_id = fields.Many2one('opinion.relative', string='Relative', required=True)
    name = fields.Char(string='Name', required=True)
    relationship_id = fields.Many2one('opinion.relationship', string='Relationship', required=True)
    address = fields.Text(string='Address')
    birth_date = fields.Date(string='Birth Date')

    @api.onchange('relative_id')
    def _onchange_relative_id(self):
        if self.relative_id:
            self.name = self.relative_id.name
            self.relationship_id = self.relative_id.relationship_id
            self.address = self.relative_id.address
            self.birth_date = self.relative_id.birth_date

    def action_update_relative(self):
        self.ensure_one()
        self.relative_id.write({
            'name': self.name,
            'relationship_id': self.relationship_id.id,
            'address': self.address,
            'birth_date': self.birth_date,
        })
        return {'type': 'ir.actions.act_window_close'}
