from odoo import models, fields, api
import csv
import base64

class AtomDataMigration(models.Model):
    _name = 'atom.data.migration'
    _description = 'Atom Data Migration'

    name = fields.Char(string='Migration Name', required=True)
    file = fields.Binary(string='CSV File', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('failed', 'Failed')
    ], string='State', default='draft')
    log = fields.Text(string='Migration Log')

    def migrate_data(self):
        self.ensure_one()
        self.state = 'in_progress'
        self.log = 'Starting migration...\n'

        try:
            csv_data = base64.b64decode(self.file).decode('utf-8').splitlines()
            reader = csv.DictReader(csv_data)
            
            for row in reader:
                atom = self.env['atom.atom'].create({'name': row['name']})
                for element in self.env['atom.element'].search([]):
                    if row.get(element.name):
                        values = row[element.name].split(',')
                        if len(values) == 3:
                            self.env['atom.element.value'].create({
                                'atom_id': atom.id,
                                'element_id': element.id,
                                'value1': float(values[0]),
                                'value2': float(values[1]),
                                'value3': float(values[2]),
                            })

                self.log += f"Migrated atom: {row['name']}\n"
                self._cr.commit()  # Commit after each atom to avoid long transactions

            self.state = 'done'
            self.log += 'Migration completed successfully.'
        except Exception as e:
            self.state = 'failed'
            self.log += f'Migration failed: {str(e)}'

        self._cr.commit()