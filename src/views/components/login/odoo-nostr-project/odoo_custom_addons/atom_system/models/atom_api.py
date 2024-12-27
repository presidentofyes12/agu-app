from odoo import models, api
from odoo.exceptions import ValidationError

class AtomAPI(models.AbstractModel):
    _name = 'atom.api'
    _description = 'Atom API'

    @api.model
    def create_atom(self, values):
        return self.env['atom.atom'].create(values)

    @api.model
    def read_atom(self, atom_id):
        return self.env['atom.atom'].browse(atom_id).read()

    @api.model
    def update_atom(self, atom_id, values):
        atom = self.env['atom.atom'].browse(atom_id)
        return atom.write(values)

    @api.model
    def delete_atom(self, atom_id):
        atom = self.env['atom.atom'].browse(atom_id)
        return atom.unlink()

    @api.model
    def search_atoms(self, domain):
        return self.env['atom.atom'].search(domain)

    @api.model
    def create_element_value(self, atom_id, element_id, values):
        atom = self.env['atom.atom'].browse(atom_id)
        element = self.env['atom.element'].browse(element_id)
        return self.env['atom.element.value'].create({
            'atom_id': atom.id,
            'element_id': element.id,
            **values
        })

    @api.model
    def update_element_value(self, value_id, values):
        value = self.env['atom.element.value'].browse(value_id)
        return value.write(values)

class AtomAPI(models.AbstractModel):
    _inherit = 'atom.api'

    @api.model
    def advanced_search(self, criteria):
        domain = []
        for criterion in criteria:
            element = self.env['atom.element'].search([('name', '=', criterion['element'])])
            if not element:
                raise ValidationError(f"Element {criterion['element']} not found")
            
            value_domain = [
                ('element_id', '=', element.id),
                '|', '|',
                ('value1', criterion['operator'], criterion['value']),
                ('value2', criterion['operator'], criterion['value']),
                ('value3', criterion['operator'], criterion['value'])
            ]
            
            atom_ids = self.env['atom.element.value'].search(value_domain).mapped('atom_id')
            domain.append(('id', 'in', atom_ids.ids))

        return self.env['atom.atom'].search(domain)