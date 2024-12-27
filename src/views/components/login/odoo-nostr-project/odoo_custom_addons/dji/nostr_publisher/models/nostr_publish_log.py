from odoo import models, fields, api, _
import logging
import json

_logger = logging.getLogger(__name__)

class NostrPublishLog(models.Model):
    _name = 'nostr.publish.log'
    _description = 'Nostr Publish Log'

    event_id = fields.Char(string='Event ID')
    success_count = fields.Integer(string='Successful Publishes')
    total_relays = fields.Integer(string='Total Relays')
    results = fields.Text(string='Publish Results')

    @api.model
    def create(self, vals):
        log = super(NostrPublishLog, self).create(vals)
        _logger.info(f"Created new Nostr publish log: Event ID {log.event_id}")
        return log

    def write(self, vals):
        result = super(NostrPublishLog, self).write(vals)
        for log in self:
            _logger.info(f"Updated Nostr publish log: Event ID {log.event_id}")
        return result

    def get_results_as_dict(self):
        self.ensure_one()
        try:
            return json.loads(self.results)
        except json.JSONDecodeError:
            _logger.error(f"Failed to parse results JSON for publish log: Event ID {self.event_id}")
            return {}
