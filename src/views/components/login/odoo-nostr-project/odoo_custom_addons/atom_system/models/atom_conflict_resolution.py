from odoo import models, fields, api
from odoo.exceptions import UserError

class AtomConflictResolution(models.Model):
    _name = 'atom.conflict.resolution'
    _description = 'Atom Conflict Resolution'

    atom_id = fields.Many2one('atom.atom', string='Atom', required=True)
    element_id = fields.Many2one('atom.element', string='Element', required=True)
    local_value = fields.Text(string='Local Value')
    remote_value = fields.Text(string='Remote Value')
    resolution = fields.Selection([
        ('local', 'Keep Local'),
        ('remote', 'Accept Remote'),
        ('manual', 'Manual Resolution')
    ], string='Resolution', required=True)
    resolved_value = fields.Text(string='Resolved Value')
    resolved_by = fields.Many2one('res.users', string='Resolved By')
    resolved_date = fields.Datetime(string='Resolved Date')

    @api.model
    def resolve_conflict(self, atom_id, element_id, local_value, remote_value):
        conflict = self.create({
            'atom_id': atom_id,
            'element_id': element_id,
            'local_value': local_value,
            'remote_value': remote_value,
        })
        
        if local_value == remote_value:
            conflict.write({
                'resolution': 'local',
                'resolved_value': local_value,
                'resolved_by': self.env.user.id,
                'resolved_date': fields.Datetime.now(),
            })
        else:
            # Notify admin for manual resolution
            self.env['mail.message'].create({
                'model': 'atom.conflict.resolution',
                'res_id': conflict.id,
                'message_type': 'notification',
                'body': f'Conflict detected for Atom {atom_id}, Element {element_id}. Manual resolution required.',
            })

        return conflict

class AtomDistributedAPI(models.AbstractModel):
    _inherit = 'atom.distributed.api'

    @api.model
    def sync_atom(self, atom_id, remote_data):
        atom = self.env['atom.atom'].browse(atom_id)
        for element_value in remote_data['element_values']:
            local_value = atom.element_values.filtered(lambda v: v.element_id.id == element_value['element_id'])
            if local_value:
                if local_value.write_date > element_value['write_date']:
                    # Local is newer, keep local
                    continue
                elif local_value.write_date < element_value['write_date']:
                    # Remote is newer, update local
                    local_value.write(element_value)
                else:
                    # Same write_date, check for conflicts
                    if local_value.value1 != element_value['value1'] or \
                       local_value.value2 != element_value['value2'] or \
                       local_value.value3 != element_value['value3']:
                        self.env['atom.conflict.resolution'].resolve_conflict(
                            atom_id, element_value['element_id'],
                            f"{local_value.value1}, {local_value.value2}, {local_value.value3}",
                            f"{element_value['value1']}, {element_value['value2']}, {element_value['value3']}"
                        )
            else:
                # New element value from remote, create locally
                self.env['atom.element.value'].create({
                    'atom_id': atom_id,
                    **element_value
                })