from odoo import models, fields, api
from datetime import datetime

class Relative(models.Model):
    _name = 'opinion.relative'
    _description = 'Family Relative'

    name = fields.Char(string='Name', required=True)
    relationship_id = fields.Many2one('opinion.relationship', string='Relationship', required=True)
    address = fields.Text(string='Address')
    birth_date = fields.Date(string='Birth Date')
    user_id = fields.Many2one('res.users', string='Related User', default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if 'birth_date' in vals and isinstance(vals['birth_date'], str):
            vals['birth_date'] = datetime.strptime(vals['birth_date'], "%Y-%m-%d").date()
        return super(Relative, self).create(vals)

    def write(self, vals):
        if 'birth_date' in vals and isinstance(vals['birth_date'], str):
            vals['birth_date'] = datetime.strptime(vals['birth_date'], "%Y-%m-%d").date()
        return super(Relative, self).write(vals)
