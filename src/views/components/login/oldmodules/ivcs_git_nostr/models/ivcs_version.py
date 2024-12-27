from odoo import models, fields, api

class IVCSVersion(models.Model):
    _name = 'ivcs.version'
    _description = 'IVCS Version'

    name = fields.Char(string='Version Name', required=True)
    description = fields.Text(string='Description')
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True, ondelete='cascade')
    commit_id = fields.Many2one('ivcs.commit', string='Associated Commit')
    create_date = fields.Datetime(string='Created On', readonly=True, default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        version = super(IVCSVersion, self).create(vals)
        if not version.item_id.current_version_id:
            version.item_id.current_version_id = version.id
        return version

    @api.depends('name', 'item_id.name')
    def name_get(self):
        result = []
        for version in self:
            name = f"{version.item_id.name} - {version.name}"
            result.append((version.id, name))
        return result
