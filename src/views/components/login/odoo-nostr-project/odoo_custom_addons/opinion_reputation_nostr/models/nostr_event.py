from odoo import models, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class NostrEvent(models.AbstractModel):
    _name = 'opinion.nostr.event'
    _description = 'Nostr Event for Opinion Reputation'

    @api.model
    def create_prediction_event(self, prediction):
        content = json.dumps({
            'question_id': prediction.question_id.id,
            'question_text': prediction.question_id.text,
            'answer': prediction.answer,
            'confidence': prediction.confidence
        })
        
        try:
            nostr_event = self.env['nostr.event']
            event = nostr_event.create_event(
                kind=1,  # You might want to use a custom event kind for predictions
                content=content,
                tags=[['p', prediction.user_id.nostr_public_key]],
                private_key=prediction.user_id.nostr_private_key
            )
            
            nostr_event.publish_event(event)
            _logger.info(f"Nostr event created and published for prediction {prediction.id}")
        except AttributeError:
            _logger.warning("Nostr bridge not available. Prediction event not published to Nostr.")
        except Exception as e:
            _logger.error(f"Error creating Nostr event: {str(e)}")
            raise UserError(_("Failed to create Nostr event: %s") % str(e))
