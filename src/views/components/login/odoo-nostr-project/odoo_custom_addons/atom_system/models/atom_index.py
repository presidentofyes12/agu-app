from odoo import models, fields, api

class AtomUsagePattern(models.Model):
    _name = 'atom.usage.pattern'
    _description = 'Atom Usage Pattern'

    element_id = fields.Many2one('atom.element', string='Element', required=True)
    usage_count = fields.Integer(string='Usage Count')
    last_used = fields.Datetime(string='Last Used')

    def create_index(self):
        self.ensure_one()
        index_name = f'atom_element_value_{self.element_id.id}_idx'
        self.env.cr.execute(f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON atom_element_value (element_id, value1, value2, value3)
            WHERE element_id = {self.element_id.id}
        """)

class AtomAPI(models.AbstractModel):
    _inherit = 'atom.api'

    @api.model
    def track_element_usage(self, element_id):
        pattern = self.env['atom.usage.pattern'].search([('element_id', '=', element_id)], limit=1)
        if pattern:
            pattern.write({
                'usage_count': pattern.usage_count + 1,
                'last_used': fields.Datetime.now(),
            })
        else:
            self.env['atom.usage.pattern'].create({
                'element_id': element_id,
                'usage_count': 1,
                'last_used': fields.Datetime.now(),
            })

        if pattern.usage_count % 100 == 0:  # Create index every 100 uses
            pattern.create_index()