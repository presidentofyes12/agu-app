from odoo import models, fields, api

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

# Example of creating documentation
def _create_example_documentation(self):
    self.env['atom.documentation'].create({
        'name': 'Atom API Reference',
        'type': 'api',
        'content': '''
        <h1>Atom API Reference</h1>
        <h2>create_atom(values)</h2>
        <p>Creates a new atom with the given values.</p>
        <h2>read_atom(atom_id)</h2>
        <p>Reads an atom with the given ID.</p>
        <h2>update_atom(atom_id, values)</h2>
        <p>Updates an atom with the given ID using the provided values.</p>
        <h2>delete_atom(atom_id)</h2>
        <p>Deletes an atom with the given ID.</p>
        ''',
        'version': '1.0'
    })