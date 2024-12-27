from odoo import models, fields, api, _
import json
import time
import logging

_logger = logging.getLogger(__name__)

class SubmitEventWizard(models.TransientModel):
    _name = 'submit.event.wizard'
    _description = 'Submit Nostr Event Wizard'

    publisher_id = fields.Many2one('nostr.publisher', string='Publisher', required=True)
    content = fields.Text(string='Event Content', required=True)
    kind = fields.Selection([
        ('1', 'Text Note'),
        ('3', 'Contacts'),
        ('7', 'Reaction'),
        ('40', 'Channel Creation'),
        ('42', 'Channel Message'),
        ('1984', 'Reporting'),
        ('9734', 'Zap Request'),
        ('10002', 'Relay List Metadata'),
    ], string='Event Kind', default='1', required=True)
    tag_key = fields.Char(string='Tag Key')
    tag_value = fields.Char(string='Tag Value')
    tags = fields.Text(string='Tags', default='[]')
    attachment = fields.Binary(string='Attachment')
    attachment_name = fields.Char(string='Attachment Name')

    @api.model
    def default_get(self, fields):
        res = super(SubmitEventWizard, self).default_get(fields)
        if 'publisher_id' in fields and not res.get('publisher_id'):
            active_id = self._context.get('active_id')
            if active_id:
                res['publisher_id'] = active_id
        return res

    @api.onchange('tag_key', 'tag_value')
    def _onchange_tag(self):
        if self.tag_key and self.tag_value:
            tags = json.loads(self.tags)
            tags.append([self.tag_key, self.tag_value])
            self.tags = json.dumps(tags)
            self.tag_key = False
            self.tag_value = False

    def submit_event(self):
        self.ensure_one()
        _logger.info(f"Starting submit_event with content: {self.content[:50]}...")
        try:
            publisher = self.env['nostr.publisher'].browse(self.publisher_id.id)
            _logger.info(f"Publisher found: {publisher.name}")
            
            _logger.info(f"Preparing event data - Kind: {self.kind}, Tags: {self.tags}")
            event_data = {
                'content': self.content,
                'kind': int(self.kind),
                'tags': json.loads(self.tags)
            }
            _logger.info(f"Calling publish_event with data: {event_data}")
            
            success = publisher.publish_event(**event_data)
            _logger.info(f"Result from publish_event: {success}")
            
            if success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Event Submitted'),
                        'message': _('Event successfully published.'),
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': _('Failed to publish event.'),
                        'type': 'danger',
                    }
                }
        except Exception as e:
            _logger.exception(f"Exception in submit_event: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to publish event: %s') % str(e),
                    'type': 'danger',
                }
            }
