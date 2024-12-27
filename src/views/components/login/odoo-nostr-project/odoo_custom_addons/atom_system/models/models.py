from odoo import models, fields, api
from odoo.exceptions import ValidationError
import json
from cryptography.fernet import Fernet

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

class AtomElementValue(models.Model):
    _name = 'atom.element.value'
    _description = 'Atom Element Value'

    atom_id = fields.Many2one('atom.atom', string='Atom', required=True)
    element_id = fields.Many2one('atom.element', string='Element', required=True)
    value1 = fields.Float(string='Value 1')
    value2 = fields.Float(string='Value 2')
    value3 = fields.Float(string='Value 3')
    sum = fields.Float(string='Sum', compute='_compute_sum', store=True)
    encryption_key = fields.Char(string='Encryption Key')

    @api.depends('value1', 'value2', 'value3')
    def _compute_sum(self):
        for record in self:
            record.sum = record.value1 + record.value2 + record.value3

    @api.model
    def create(self, vals):
        if vals.get('encryption_key'):
            fernet = Fernet(vals['encryption_key'].encode())
            for field in ['value1', 'value2', 'value3']:
                if vals.get(field):
                    vals[field] = fernet.encrypt(str(vals[field]).encode()).decode()
        return super(AtomElementValue, self).create(vals)

    def read(self, fields=None, load='_classic_read'):
        result = super(AtomElementValue, self).read(fields, load)
        for record in result:
            if record.get('encryption_key'):
                fernet = Fernet(record['encryption_key'].encode())
                for field in ['value1', 'value2', 'value3']:
                    if record.get(field):
                        record[field] = float(fernet.decrypt(record[field].encode()).decode())
        return result

class AtomVersion(models.Model):
    _name = 'atom.version'
    _description = 'Atom Version'

    atom_id = fields.Many2one('atom.atom', string='Atom', required=True)
    version_number = fields.Integer(string='Version Number', required=True)
    changed_by = fields.Many2one('res.users', string='Changed By', required=True)
    changed_on = fields.Datetime(string='Changed On', required=True, default=fields.Datetime.now)
    changes = fields.Text(string='Changes', required=True)

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

class DistributedNode(models.Model):
    _name = 'atom.distributed.node'
    _description = 'Distributed Node'

    name = fields.Char(string='Node Name', required=True)
    url = fields.Char(string='Node URL', required=True)
    is_active = fields.Boolean(string='Is Active', default=True)

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

class AtomDocumentation(models.Model):
    _name = 'atom.documentation'
    _description = 'Atom System Documentation'

    name = fields.Char(string='Document Name', required=True)
    type = fields.Selection([
        ('api', 'API Reference'),
        ('user_guide', 'User Guide'),
        ('architecture', 'Architectural Overview'),
        ('development', 'Development Guide')
    ], string='Document Type', required=True)
    content = fields.Html(string='Content', required=True)
    version = fields.Char(string='Version', required=True)

    @api.model
    def get_latest_doc(self, doc_type):
        return self.search([('type', '=', doc_type)], order='version desc', limit=1)

class AtomBestPractice(models.Model):
    _name = 'atom.best.practice'
    _description = 'Atom System Best Practice'

    name = fields.Char(string='Practice Name', required=True)
    category = fields.Selection([
        ('query_optimization', 'Query Optimization'),
        ('data_management', 'Data Management'),
        ('scaling', 'Scaling'),
        ('performance', 'Performance')
    ], string='Category', required=True)
    description = fields.Text(string='Description', required=True)
    example = fields.Text(string='Example')

    @api.model
    def get_best_practices(self, category=None):
        domain = []
        if category:
            domain.append(('category', '=', category))
        return self.search(domain).read(['name', 'description', 'example'])