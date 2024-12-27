import requests
import websocket
import time  # Add this import
from odoo import models, api
from websocket._exceptions import WebSocketConnectionClosedException
from odoo.exceptions import UserError
from nostr.event import Event
from nostr.key import PrivateKey
from nostr.relay_manager import RelayManager
import logging

_logger = logging.getLogger(__name__)

MAX_CONCURRENT_RELAYS = 10

class NostrAdapter(models.AbstractModel):
    _name = 'nostr.adapter'
    _description = 'Nostr Adapter'

    @api.model
    def get_relay_manager(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        relay_urls = ICPSudo.get_param('nostr_bridge.relay_urls', '').split(',')
        if not relay_urls:
            raise UserError("Nostr relay URL is not configured. Please set it in the settings.")
        _logger.info(f"Nostr relay URLs: {relay_urls}")
        relay_manager = RelayManager()
        for url in relay_urls:
            url = url.strip()
            if url:  # Only add non-empty URLs
                _logger.info(f"Adding relay: {url}")
                relay_manager.add_relay(url)
        return relay_manager

    @api.model
    def publish_event(self, event_data, max_retries=3, retry_delay=2):
        relay_urls = self._get_relay_urls()
        
        for attempt in range(max_retries):
            try:
                private_key = PrivateKey.from_nsec(self.env.user.nostr_private_key)
                public_key = private_key.public_key.hex()
                
                event = Event(
                    kind=event_data['kind'],
                    content=event_data['content'],
                    tags=event_data.get('tags', []),
                    public_key=public_key
                )
                private_key.sign_event(event)
                
                for i in range(0, len(relay_urls), MAX_CONCURRENT_RELAYS):
                    batch = relay_urls[i:i+MAX_CONCURRENT_RELAYS]
                    relay_manager = RelayManager()
                    for url in batch:
                        relay_manager.add_relay(url)
                    
                    try:
                        relay_manager.open_connections({"write": True})
                        time.sleep(1)  # Give some time for connections to establish
                        
                        publish_result = relay_manager.publish_event(event)
                        _logger.info(f"Relay publish response: {publish_result}")
                    except Exception as e:
                        _logger.error(f"Error publishing event to Nostr: {str(e)}")
                    finally:
                        relay_manager.close_connections()
                
                return True
            except Exception as e:
                _logger.exception(f"Error publishing event to Nostr: {str(e)}")
                time.sleep(retry_delay)
        
        _logger.error("Failed to publish event after multiple attempts")
        return False

    def _get_relay_urls(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        relay_urls = ICPSudo.get_param('nostr_bridge.relay_urls', '').split(',')
        return [url.strip() for url in relay_urls if url.strip()]
