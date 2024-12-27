from odoo import models, fields, api

class AtomGuideline(models.Model):
    _name = 'atom.guideline'
    _description = 'Atom System Guideline'

    name = fields.Char(string='Guideline Name', required=True)
    category = fields.Selection([
        ('data_type', 'New Data Type'),
        ('relationship', 'New Relationship'),
        ('extension', 'System Extension'),
    ], string='Category', required=True)
    description = fields.Text(string='Description', required=True)
    example_code = fields.Text(string='Example Code')

    @api.model
    def get_guidelines(self, category=None):
        domain = []
        if category:
            domain.append(('category', '=', category))
        return self.search(domain).read(['name', 'description', 'example_code'])

# Example guideline
def _create_example_guideline(self):
    self.env['atom.guideline'].create({
        'name': 'Adding a New Data Type',
        'category': 'data_type',
        'description': '''
        To add a new data type:
        1. Determine which of the 108 elements will represent the new type.
        2. Update the ElementMapping model to include the new semantic meaning.
        3. If necessary, create a new model that extends AtomElementValue for specialized behavior.
        4. Update any relevant APIs or interfaces to handle the new type.
        ''',
        'example_code': '''
    class NewDataTypeValue(models.Model):
        _inherit = 'atom.element.value'
        
        specialized_field = fields.Char(string='Specialized Field')

        @api.model
        def create(self, vals):
            if vals.get('element_id') == self.env.ref('my_module.new_data_type_element').id:
                # Specialized handling for the new data type
                pass
            return super(NewDataTypeValue, self).create(vals)
        '''
    })