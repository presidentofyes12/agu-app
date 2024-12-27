from odoo import models, fields, api

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

# Example best practices
def _create_example_best_practices(self):
    self.env['atom.best.practice'].create({
        'name': 'Use Indexed Search for Large Datasets',
        'category': 'query_optimization',
        'description': 'When searching large datasets, always use indexed fields in your domain to improve query performance.',
        'example': "self.env['atom.atom'].search([('indexed_field', '=', value)])"
    })

    self.env['atom.best.practice'].create({
        'name': 'Batch Processing for Large Data Operations',
        'category': 'data_management',
        'description': 'When performing operations on large datasets, use batch processing to reduce memory usage and improve performance.',
        'example': """
        def process_in_batches(self, batch_size=1000):
            offset = 0
            while True:
                batch = self.search([], limit=batch_size, offset=offset)
                if not batch:
                    break
                for record in batch:
                    # Process record
                offset += batch_size
                self.env.cr.commit()
        """
    })

    self.env['atom.best.practice'].create({
        'name': 'Use Prefetching for Related Records',
        'category': 'performance',
        'description': 'When accessing related records, use prefetching to reduce the number of database queries.',
        'example': "atoms = self.env['atom.atom'].browse(ids).prefetch_related('element_values')"
    })