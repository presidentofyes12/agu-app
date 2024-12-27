from odoo import models, fields, api
from odoo.tools.cache import ormcache

class AtomCache(models.AbstractModel):
    _name = 'atom.cache'
    _description = 'Atom Cache'

    @api.model
    @ormcache('atom_id')
    def get_atom(self, atom_id):
        return self.env['atom.atom'].browse(atom_id).read()[0]

    @api.model
    @ormcache('element_id', 'value1', 'value2', 'value3')
    def search_atom_by_element(self, element_id, value1, value2, value3):
        return self.env['atom.element.value'].search([
            ('element_id', '=', element_id),
            ('value1', '=', value1),
            ('value2', '=', value2),
            ('value3', '=', value3)
        ]).mapped('atom_id').ids

    @api.model
    def clear_atom_cache(self, atom_id):
        self.clear_caches()

class Atom(models.Model):
    _inherit = 'atom.atom'

    def write(self, vals):
        result = super(Atom, self).write(vals)
        self.env['atom.cache'].clear_atom_cache(self.id)
        return result