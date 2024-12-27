# -*- coding: utf-8 -*-

# Have program dynamically select 9 relays to use
# Any relay that fails, blacklist for 9 days- if it fails after 9 days, multiply length by 9, etc.

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
from nostr.relay_manager import RelayManager
from nostr.event import Event
from nostr.key import PrivateKey
import time
import asyncio
import websockets
import json
from nostr.message_type import ClientMessageType

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gitlab_url = fields.Char(string="GitLab URL", config_parameter='gitlab_nostr_bridge.gitlab_url')
    gitlab_private_token = fields.Char(string="GitLab Private Token", config_parameter='gitlab_nostr_bridge.gitlab_private_token')
    use_alternative_publish = fields.Boolean(string="Use Alternative Publish Method", config_parameter='use_alternative_publish')
    nostr_relay_urls = fields.Char(string="Nostr Relay URLs", config_parameter='nostr_bridge.relay_urls')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('gitlab_nostr_bridge.gitlab_url', self.gitlab_url)
        self.env['ir.config_parameter'].set_param('gitlab_nostr_bridge.gitlab_private_token', self.gitlab_private_token)
        self.env['ir.config_parameter'].set_param('use_alternative_publish', str(self.use_alternative_publish))
        self.env['ir.config_parameter'].set_param('nostr_bridge.relay_urls', self.nostr_relay_urls)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            gitlab_url=params.get_param('gitlab_nostr_bridge.gitlab_url', default=''),
            gitlab_private_token=params.get_param('gitlab_nostr_bridge.gitlab_private_token', default=''),
            use_alternative_publish=params.get_param('use_alternative_publish', default=False) == 'True',
            nostr_relay_urls=params.get_param('nostr_bridge.relay_urls', default=''),
        )
        return res

    def test_gitlab_connection(self):
        self.ensure_one()
        if not self.gitlab_url or not self.gitlab_private_token:
            raise UserError(_("GitLab URL and Private Token must be set."))

        try:
            response = requests.get(
                f"{self.gitlab_url.rstrip('/')}/api/v4/user",
                headers={"Private-Token": self.gitlab_private_token},
                timeout=10
            )
            response.raise_for_status()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Connection Successful"),
                    'message': _("Connected to GitLab successfully."),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to connect to GitLab: {str(e)}")
            raise UserError(_("Failed to connect to GitLab: %s") % str(e))

    @api.onchange('use_alternative_publish')
    def _onchange_use_alternative_publish(self):
        if self.use_alternative_publish:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("Using the alternative publish method may affect the way Nostr events are sent. Please ensure your relays are compatible with this method.")
                }
            }

    def action_clear_gitlab_token(self):
        self.ensure_one()
        self.gitlab_private_token = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("GitLab Token Cleared"),
                'message': _("The GitLab private token has been cleared."),
                'type': 'warning',
                'sticky': False,
            }
        }

    def test_nostr_connection(self):
        self.ensure_one()
        user = self.env.user
        if not user.nostr_private_key:
            raise UserError(_("Nostr private key is not set for the current user. Please generate it first."))

        relay_urls = self.nostr_relay_urls.split(',') if self.nostr_relay_urls else []
        if not relay_urls:
            raise UserError(_("No Nostr relay URLs configured. Please set them in the settings."))

        _logger.info(f"Starting Nostr connection test with {len(relay_urls)} relays")

        try:
            # Enable debug logging for nostr
            logging.getLogger('nostr').setLevel(logging.DEBUG)

            # Create a test event
            private_key = PrivateKey.from_nsec(user.nostr_private_key)
            pub_key = private_key.public_key.hex()
            event = Event(
                public_key=pub_key,
                created_at=int(time.time()),
                kind=1,
                tags=[],
                content="Test connection from Odoo"
            )
            private_key.sign_event(event)
            _logger.info(f"Created test event with ID: {event.id}")

            # Test publishing to relays
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self._test_nostr_relays(relay_urls, event))

            _logger.info(f"Raw results data: {str(results)}");

            # Process results
            successes = [result for result in results if result['success']]
            failures = [result for result in results if not result['success']]

            _logger.info(f"Test completed. Successful connections: {len(successes)}, Failed connections: {len(failures)}")

            if successes:
                message = f"Successfully connected to {len(successes)} out of {len(relay_urls)} relays."
                if failures:
                    message += f"\nFailed to connect to {len(failures)} relays."
                message_type = 'warning' if failures else 'success'
            else:
                message = "Failed to publish the test event to any relay.\n"
                message += "\n".join([f"{result['url']}: {result['message']}" for result in failures])
                message_type = 'danger'

            _logger.info(f"Test result message: {message}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Test Results"),
                    'message': message,
                    'type': message_type,
                    'sticky': True,
                }
            }

        except Exception as e:
            _logger.error(f"Error in test_nostr_connection: {str(e)}", exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("An error occurred while testing Nostr connection: %s") % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    async def publish_with_limit(self, semaphore, url, event):
        async with semaphore:
            try:
                _logger.info(f"Attempting to connect to relay: {url}")
                async with websockets.connect(url.strip(), ping_interval=None) as websocket:
                    message = event.to_message()  # Use to_message() instead of to_dict()
                    _logger.info(f"Sending message to {url}: {message[:100]}...")  # Log first 100 chars of message
                    await websocket.send(message)
                    _logger.info(f"Message sent to {url}, waiting for response...")
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    _logger.info(f"Received response from {url}: {response}")
                    if json.loads(response)[0] == "OK":
                        return {'success': True, 'url': url, 'message': f"Successfully published to {url}"}
                    else:
                        return {'success': False, 'url': url, 'message': f"Failed to publish to {url}: {response}"}
            except Exception as e:
                _logger.error(f"Unexpected error while connecting to {url}: {str(e)}", exc_info=True)
                return {'success': False, 'url': url, 'message': f"Failed to publish to {url}: {str(e)}"}

    async def _test_nostr_relays(self, relay_urls, event, timeout=10):
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent connections
        _logger.info(f"Testing {len(relay_urls)} relays with a concurrency limit of 10")
        tasks = [self.publish_with_limit(semaphore, url, event) for url in relay_urls]
        results = await asyncio.gather(*tasks)
        _logger.info(f"Completed testing all relays")
        return results
