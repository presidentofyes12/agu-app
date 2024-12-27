from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class IVCSMetadata(models.Model):
    _name = 'ivcs.metadata'
    _description = 'IVCS Metadata'

    key = fields.Char(string='Key', required=True)
    value = fields.Char(string='Value', required=True)
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', ondelete='cascade')
    version_id = fields.Many2one('ivcs.version', string='IVCS Version', ondelete='cascade')

    @api.constrains('item_id', 'version_id')
    def _check_item_or_version(self):
        for record in self:
            if not record.item_id and not record.version_id:
                raise ValidationError(_("Metadata must be associated with either an IVCS Item or an IVCS Version."))
            if record.item_id and record.version_id:
                raise ValidationError(_("Metadata can't be associated with both an IVCS Item and an IVCS Version simultaneously."))

    @api.constrains('key')
    def _check_key_uniqueness(self):
        for record in self:
            domain = [('key', '=', record.key)]
            if record.item_id:
                domain.append(('item_id', '=', record.item_id.id))
            elif record.version_id:
                domain.append(('version_id', '=', record.version_id.id))
            if self.search_count(domain) > 1:
                raise ValidationError(_("Metadata key must be unique for each IVCS Item or Version."))

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.key}: {record.value}"
            if record.item_id:
                name = f"{record.item_id.name} - {name}"
            elif record.version_id:
                name = f"{record.version_id.name} - {name}"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        record = super(IVCSMetadata, self).create(vals)
        self._update_last_modified(record)
        return record

    def write(self, vals):
        result = super(IVCSMetadata, self).write(vals)
        self._update_last_modified(self)
        return result

    def _update_last_modified(self, records):
        for record in records:
            if record.item_id:
                record.item_id.write({'last_metadata_update': fields.Datetime.now()})
            elif record.version_id:
                record.version_id.write({'last_metadata_update': fields.Datetime.now()})
