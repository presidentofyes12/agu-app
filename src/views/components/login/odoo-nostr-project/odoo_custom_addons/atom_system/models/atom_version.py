from odoo import models, fields, api
import json

class AtomVersion(models.Model):
    _name = 'atom.version'
    _description = 'Atom Version'

    atom_id = fields.Many2one('atom.atom', string='Atom', required=True)
    version_number = fields.Integer(string='Version Number', required=True)
    changed_by = fields.Many2one('res.users', string='Changed By', required=True)
    changed_on = fields.Datetime(string='Changed On', required=True, default=fields.Datetime.now)
    changes = fields.Text(string='Changes', required=True)

class Atom(models.Model):
    _inherit = 'atom.atom'

    current_version = fields.Integer(string='Current Version', default=1)
    version_ids = fields.One2many('atom.version', 'atom_id', string='Versions')

    def write(self, vals):
        result = super(Atom, self).write(vals)
        for record in self:
            self.env['atom.version'].create({
                'atom_id': record.id,
                'version_number': record.current_version + 1,
                'changed_by': self.env.user.id,
                'changes': json.dumps(vals)
            })
            record.current_version += 1
        return result