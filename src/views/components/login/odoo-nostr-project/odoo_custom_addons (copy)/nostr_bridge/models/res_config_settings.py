import requests
import json
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_nostr_relays(self):
        return self._get_top_nostr_relays()

    @api.model
    def _get_top_nostr_relays(self, limit=108):
        url = "https://api.nostr.watch/v1/online"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            _logger.info(f"Response status code: {response.status_code}")
            
            data = response.json()
            #_logger.info(f"API response (first 108 items): {json.dumps(data)[:1000]}")
            _logger.info(f"API response (first 108 items): {data[:108]}")
            
            relays = data[:108]
            _logger.info(f"Number of relay links found: {len(relays)}")
            _logger.info(f"Extracted relays (first 5): {relays[:5]}")
            
            relay_urls = ",".join(relays)
            return relay_urls
        except requests.RequestException as e:
            _logger.error(f"Error fetching Nostr relays: {e}")
            return "wss://nostr-relay.app,wss://nos.lol,wss://relay.snort.social,wss://relay.nostr.net"

    nostr_relay_urls = fields.Char(
        string="Nostr Relay URLs", 
        config_parameter='nostr_bridge.relay_urls',
        default=_default_nostr_relays
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        relay_urls = ICPSudo.get_param('nostr_bridge.relay_urls')
        if not relay_urls:
            relay_urls = self._get_top_nostr_relays()
            ICPSudo.set_param('nostr_bridge.relay_urls', relay_urls)
            _logger.info(f"Set new relay URLs: {relay_urls[:100]}...")  # Log first 100 characters
        else:
            _logger.info(f"Using existing relay URLs: {relay_urls[:100]}...")  # Log first 100 characters
        
        res.update(nostr_relay_urls=relay_urls)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        if self.nostr_relay_urls:
            ICPSudo.set_param('nostr_bridge.relay_urls', self.nostr_relay_urls)
            _logger.info(f"Updated relay URLs: {self.nostr_relay_urls[:100]}...")  # Log first 100 characters
        else:
            default_urls = self._get_top_nostr_relays()
            ICPSudo.set_param('nostr_bridge.relay_urls', default_urls)
            _logger.info(f"Set default relay URLs: {default_urls[:100]}...")  # Log first 100 characters
