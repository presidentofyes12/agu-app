from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Creating new mail messages")
        messages = super(MailMessage, self).create(vals_list)
        for message in messages:
            self._publish_to_nostr(message)
        return messages

    def _publish_to_nostr(self, message):
        try:
            nostr_adapter = self.env['nostr.adapter'].sudo()
            event_data = {
                'kind': 1,  # Text note
                'content': message.body,
                'tags': [
                    ['e', str(message.parent_id.id)] if message.parent_id else [],
                    ['p', message.author_id.nostr_public_key] if message.author_id and message.author_id.nostr_public_key else [],
                    ['client', 'Odoo Nostr Bridge'],
                ],
            }
            result = nostr_adapter.publish_event(event_data)
            if result:
                _logger.info(f"Successfully published message {message.id} to Nostr")
            else:
                _logger.warning(f"Failed to publish message {message.id} to Nostr")
        except Exception as e:
            _logger.exception(f"Error publishing message {message.id} to Nostr: {str(e)}")
