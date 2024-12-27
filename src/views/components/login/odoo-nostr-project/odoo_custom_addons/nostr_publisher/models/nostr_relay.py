from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class NostrRelay(models.Model):
    _name = 'nostr.relay'
    _description = 'Nostr Relay'

    publisher_id = fields.Many2one('nostr.publisher', string='Publisher')
    url = fields.Char(string='URL', required=True)
    is_active = fields.Boolean(string='Is Active', default=True)
    last_connection = fields.Datetime(string='Last Connection')
    connection_failures = fields.Integer(string='Connection Failures', default=0)
    response_time = fields.Float(string='Response Time (ms)', default=0)

    def test_connection(self):
        self.ensure_one()
        is_active, response_time = self.env['nostr.publisher']._test_relay_connection(self.url)
        if is_active:
            self.write({
                'is_active': True,
                'last_connection': fields.Datetime.now(),
                'connection_failures': 0,
                'response_time': response_time,
            })
        else:
            self.write({
                'is_active': False,
                'connection_failures': self.connection_failures + 1,
            })
        return is_active

    @api.model
    def create(self, vals):
        relay = super(NostrRelay, self).create(vals)
        relay.test_connection()
        return relay

    def write(self, vals):
        result = super(NostrRelay, self).write(vals)
        if 'url' in vals:
            self.test_connection()
        return result

    def action_test_connection(self):
        self.ensure_one()
        is_active = self.test_connection()
        message = _("Connection successful") if is_active else _("Connection failed")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Relay Connection Test"),
                'message': message,
                'sticky': False,
                'type': 'success' if is_active else 'danger',
            }
        }
