from odoo import models, fields, api

class AtomElement(models.Model):
    _name = 'atom.element'
    _description = 'Atom Element'

    name = fields.Char(string='Element Name', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    constituent1 = fields.Float(string='Constituent 1')
    constituent2 = fields.Float(string='Constituent 2')
    constituent3 = fields.Float(string='Constituent 3')
    sum = fields.Float(string='Sum', compute='_compute_sum', store=True)

    @api.depends('constituent1', 'constituent2', 'constituent3')
    def _compute_sum(self):
        for record in self:
            record.sum = record.constituent1 + record.constituent2 + record.constituent3

class Atom(models.Model):
    _name = 'atom.atom'
    _description = 'Atom'

    name = fields.Char(string='Atom Name', required=True)
    element_values = fields.One2many('atom.element.value', 'atom_id', string='Element Values')

class AtomElementValue(models.Model):
    _name = 'atom.element.value'
    _description = 'Atom Element Value'

    atom_id = fields.Many2one('atom.atom', string='Atom', required=True)
    element_id = fields.Many2one('atom.element', string='Element', required=True)
    value1 = fields.Float(string='Value 1')
    value2 = fields.Float(string='Value 2')
    value3 = fields.Float(string='Value 3')
    sum = fields.Float(string='Sum', compute='_compute_sum', store=True)

    @api.depends('value1', 'value2', 'value3')
    def _compute_sum(self):
        for record in self:
            record.sum = record.value1 + record.value2 + record.value3

class ElementMapping(models.Model):
    _name = 'atom.element.mapping'
    _description = 'Element Semantic Mapping'

    element_id = fields.Many2one('atom.element', string='Element', required=True)
    semantic_key = fields.Char(string='Semantic Key', required=True)
    description = fields.Text(string='Description')
    interpretation_rules = fields.Text(string='Interpretation Rules')

    _sql_constraints = [
        ('unique_element_semantic', 'unique(element_id, semantic_key)', 'Semantic key must be unique per element.')
    ]

class AtomLink(models.Model):
    _name = 'atom.link'
    _description = 'Atom Link'

    source_atom_id = fields.Many2one('atom.atom', string='Source Atom', required=True)
    target_atom_id = fields.Many2one('atom.atom', string='Target Atom', required=True)
    link_type = fields.Selection([
        ('parent_child', 'Parent-Child'),
        ('reference', 'Reference'),
        ('compound', 'Compound Object'),
    ], string='Link Type', required=True)
    description = fields.Text(string='Link Description')

class Atom(models.Model):
    _inherit = 'atom.atom'

    parent_links = fields.One2many('atom.link', 'target_atom_id', string='Parent Links')
    child_links = fields.One2many('atom.link', 'source_atom_id', string='Child Links')