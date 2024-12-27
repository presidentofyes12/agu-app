import logging
from odoo import models, api
from nostr.event import Event
from nostr.key import PrivateKey
import time

_logger = logging.getLogger(__name__)

class NostrAdapter(models.AbstractModel):
    _name = 'nostr.adapter'
    _description = 'Nostr Adapter'

    @api.model
    def publish_event(self, event_data, max_retries=3, retry_delay=2):
        _logger.info(f"Starting publish_event in NostrAdapter with data: {event_data}")
        
        for attempt in range(max_retries):
            try:
                _logger.info(f"Attempt {attempt + 1} of {max_retries}")
                
                _logger.info("Creating Nostr Event object")
                event = Event(
                    content=event_data['content'],
                    public_key=event_data['public_key'],
                    created_at=int(time.time()),
                    kind=event_data['kind'],
                    tags=event_data['tags']
                )
                _logger.info(f"Event created with ID: {event.id}")

                _logger.info("Signing the event")
                private_key = PrivateKey.from_nsec(self.env.user.nostr_private_key)
                private_key.sign_event(event)
                _logger.info("Event signed successfully")

                _logger.info("Initializing RelayManager")
                relay_manager = RelayManager()
                for relay_url in self._get_relay_urls():
                    _logger.info(f"Adding relay: {relay_url}")
                    relay_manager.add_relay(relay_url)

                _logger.info("Publishing event to relays")
                relay_manager.publish_event(event)
                _logger.info("Event published successfully")

                return True
            except Exception as e:
                _logger.error(f"Error in publish_event attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    _logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    _logger.error("Max retries reached. Failing.")
                    return False

    def _get_relay_urls(self):
        _logger.info("Fetching relay URLs")
        relay_urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
        relay_urls = [url.strip() for url in relay_urls if url.strip()]
        _logger.info(f"Fetched relay URLs: {relay_urls}")
        return relay_urls
