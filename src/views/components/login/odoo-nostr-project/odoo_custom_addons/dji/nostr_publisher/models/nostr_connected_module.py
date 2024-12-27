from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class NostrConnectedModule(models.Model):
    _name = 'nostr.connected.module'
    _description = 'Nostr Connected Module'

    publisher_id = fields.Many2one('nostr.publisher', string='Publisher')
    name = fields.Char(string='Module Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model')
    public_key = fields.Char(string='Public Key')
    last_sync_date = fields.Datetime(string='Last Sync Date')

    @api.model
    def create(self, vals):
        module = super(NostrConnectedModule, self).create(vals)
        _logger.info(f"Created new Nostr connected module: {module.name}")
        return module

    def write(self, vals):
        result = super(NostrConnectedModule, self).write(vals)
        for module in self:
            _logger.info(f"Updated Nostr connected module: {module.name}")
        return result

    def unlink(self):
        for module in self:
            _logger.info(f"Deleting Nostr connected module: {module.name}")
        return super(NostrConnectedModule, self).unlink()
