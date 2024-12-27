from odoo import models, fields

class IVCSMetadata(models.Model):
    _name = 'ivcs.metadata'
    _description = 'IVCS Metadata'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', ondelete='cascade')
    version_id = fields.Many2one('ivcs.version', string='IVCS Version', ondelete='cascade')
    key = fields.Char('Key', required=True)
    value = fields.Char('Value', required=True)
