from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SubmitEventWizard(models.TransientModel):
    _name = 'submit.event.wizard'
    _description = 'Submit Nostr Event Wizard'

    publisher_id = fields.Many2one('nostr.publisher', string='Publisher', required=True)
    content = fields.Text(string='Event Content', required=True)
    kind = fields.Integer(string='Event Kind', default=1)
    tags = fields.Text(string='Tags (JSON format)', default='[]')

    def action_submit_event(self):
        self.ensure_one()
        try:
            tags = json.loads(self.tags)
        except json.JSONDecodeError:
            raise UserError(_("Invalid JSON format for tags"))

        success = self.publisher_id.publish_event(self.content, kind=self.kind, tags=tags)
        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Event Submitted"),
                    'message': _("Event successfully published via GitLab Nostr Bridge."),
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Failed to publish event via GitLab Nostr Bridge."),
                    'type': 'danger',
                }
            }
