from odoo import models, fields, api

class CreateVersionWizard(models.TransientModel):
    _name = 'ivcs.create.version.wizard'
    _description = 'Create New Version Wizard'

    item_id = fields.Many2one('ivcs.item', string='Item', required=True)
    name = fields.Char('Version Name', required=True)
    description = fields.Text('Description')

    @api.model
    def default_get(self, fields):
        res = super(CreateVersionWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            item = self.env['ivcs.item'].browse(active_id)
            res['item_id'] = item.id
            last_version = item.version_ids.sorted(lambda v: v.create_date, reverse=True)[:1]
            if last_version:
                res['name'] = f"v{float(last_version.name[1:]) + 0.1:.1f}"
        return res

    def create_version(self):
        self.ensure_one()
        new_version = self.env['ivcs.version'].create({
            'item_id': self.item_id.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.item_id.current_version_id.id,
        })
        self.item_id.current_version_id = new_version.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ivcs.version',
            'res_id': new_version.id,
            'view_mode': 'form',
            'target': 'current',
        }
