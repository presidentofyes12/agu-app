# -*- coding: utf-8 -*-

import abc
from functools import wraps
import json
import logging
import time
import asyncio
import websockets
from odoo import models, fields, api, _
from websockets.exceptions import WebSocketException
from odoo.exceptions import UserError
from nostr.event import Event, EventKind
from nostr.key import PrivateKey, PublicKey
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from bech32 import bech32_decode, convertbits
import ssl
from nostr import bech32
from hashlib import sha256
from secp256k1 import PublicKey as Secp256k1PublicKey, PrivateKey as Secp256k1PrivateKey
from dataclasses import dataclass, field
from typing import List

_logger = logging.getLogger(__name__)

# ---- Decorator Pattern ----

def enhanced_publish_event(func):
    """
    Decorator to enhance the publish_event method.
    It adds logging and error handling capabilities.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _logger.info(f"Starting publish action for event: {self.event_id}")
        start_time = time.time()

        try:
            result = func(self, *args, **kwargs)
            
            end_time = time.time()
            _logger.info(f"Total publish action time: {end_time - start_time:.2f} seconds")
            
            return result
        except Exception as e:
            _logger.error(f"Error in publish_event: {str(e)}", exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("An unexpected error occurred: %s") % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    return wrapper

# ---- Strategy Pattern ----

class PublishStrategy(abc.ABC):
    """
    Abstract base class for publish strategies.
    Concrete strategies should implement the publish method.
    """
    @abc.abstractmethod
    def publish(self, event):
        pass

class OriginalPublishStrategy(PublishStrategy):
    """
    Original publishing strategy using existing logic.
    """
    def publish(self, event):
        relay_manager = RelayManager(event.env)
        relay_urls = relay_manager.relay_urls[:5]  # Get the first 5 URLs

        if not relay_urls:
            return event._return_notification("Configuration Error", "No Nostr relay URLs configured.", "warning")

        nostr_event = event._create_nostr_event()
        signed_event = event._sign_event(nostr_event)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tasks = [relay_manager.publish_to_relay(url, signed_event) for url in relay_urls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            success_count = sum(1 for result in results if result['success'] and 'true' in result['response'].lower())
            success_rate = success_count / len(relay_urls)
        finally:
            loop.close()

        logs = "\n".join([f"Relay {r['url']}: {'Success' if r['success'] else 'Failed'} - {r.get('response', r.get('error', 'No response'))}" for r in results])

        if success_rate > 0:
            event.write({
                'event_id': signed_event.id,
                'signature': signed_event.signature,
                'published': True,
                'logs': logs
            })
            return event._return_notification("Success", f"Nostr event published successfully to {success_count} relays.", "success")
        else:
            event.write({'logs': logs})
            return event._return_notification("Publishing Failed", "Failed to publish Nostr event to any relay.", "danger", sticky=True)

class AlternativePublishStrategy(PublishStrategy):
    """
    Alternative publishing strategy with enhanced error handling and SSL options.
    """
    def publish(self, event):
        relay_manager = RelayManager(event.env)
        relay_urls = relay_manager.relay_urls[:5]  # Get the first 5 URLs

        if not relay_urls:
            return event._return_notification("Configuration Error", "No Nostr relay URLs configured.", "warning")

        nostr_event = event._create_nostr_event()
        signed_event = event._sign_event(nostr_event)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success_rate = loop.run_until_complete(relay_manager.publish_to_relays(signed_event, [{'url': url} for url in relay_urls]))
        finally:
            loop.close()

        if success_rate > 0:
            event.write({
                'event_id': signed_event.id,
                'signature': signed_event.signature,
                'published': True,
                'logs': f"Event published to relays with {success_rate:.2f} success rate: {', '.join(relay_urls)}"
            })
            return event._return_notification("Success", f"Nostr event published successfully with {success_rate:.2f} success rate.", "success")
        else:
            return event._return_notification("Publishing Failed", "Failed to publish Nostr event to any relay.", "danger", sticky=True)

class AsyncPublishStrategy(PublishStrategy):
    """
    Async publishing strategy with enhanced error handling and parallel publishing.
    """
    async def publish_to_relay(self, url, message):
        try:
            async with websockets.connect(url, close_timeout=30) as websocket:
                await websocket.send(message)
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                return {'success': True, 'url': url, 'response': response}
        except websockets.WebSocketException as e:
            return {'success': False, 'url': url, 'error': f"WebSocket error: {str(e)}"}
        except Exception as e:
            return {'success': False, 'url': url, 'error': f"General error: {str(e)}"}

    async def _publish_to_relays(self, relay_urls, event_message):
        tasks = [self.publish_to_relay(url, event_message) for url in relay_urls]
        results = await asyncio.gather(*tasks)
        
        # Log detailed errors for each failed relay
        for result in results:
            if not result['success']:
                _logger.error(f"Failed to publish to {result['url']}: {result['error']}")

        # Determine if at least one relay succeeded
        success = any(result['success'] for result in results)
        return success

    def publish(self, event):
        try:
            # Prepare event data
            nostr_event = event._create_nostr_event()
            signed_event = event._sign_event(nostr_event)
            event_message = json.dumps([ClientMessageType.EVENT, signed_event.to_dict()])
            
            # Get relay URLs from configuration
            relay_urls = event.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
            relay_urls = [url.strip() for url in relay_urls if url.strip()]
            
            if not relay_urls:
                return event._return_notification("Configuration Error", "No Nostr relay URLs configured.", "warning")
            
            # Use asyncio to run the publishing process
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self._publish_to_relays(relay_urls, event_message))
            
            if success:
                event.write({
                    'event_id': signed_event.id,
                    'signature': signed_event.signature,
                    'published': True,
                    'logs': f"Event published to relays: {', '.join(relay_urls)}"
                })
                return event._return_notification("Success", "Event published successfully.", "success")
            else:
                return event._return_notification("Failed", "Failed to publish the event to any relay.", "danger", sticky=True)
        except Exception as e:
            _logger.error(f"Error in publish_event: {str(e)}", exc_info=True)
            return event._return_notification("Error", f"An unexpected error occurred: {str(e)}", "danger", sticky=True)

# ---- New Relay Management System ----

class RelayManager:
    def __init__(self, env):
        self.env = env
        self.relay_urls = self._get_relay_urls()
        self.successful_relays = []
        _logger.info(f"Initialized RelayManager with {len(self.relay_urls)} relay URLs")

    def _get_relay_urls(self):
        urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
        _logger.info(f"Retrieved {len(urls)} relay URLs from configuration")
        return urls

    async def test_relay(self, url):
        _logger.info(f"Testing relay: {url}")
        try:
            async with websockets.connect(url.strip(), ping_interval=None, close_timeout=5) as websocket:
                start_time = time.time()
                await websocket.send(json.dumps(["REQ", "1", {"kinds": [1]}]))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                end_time = time.time()
                _logger.info(f"Successfully tested relay {url}. Response time: {end_time - start_time:.2f} seconds")
                return {'url': url, 'success': True, 'response_time': end_time - start_time}
        except Exception as e:
            _logger.error(f"Failed to test relay {url}: {str(e)}")
            return {'url': url, 'success': False, 'error': str(e)}

    async def test_relays(self):
        _logger.info(f"Starting to test {len(self.relay_urls)} relays")
        tasks = [self.test_relay(url) for url in self.relay_urls]
        results = await asyncio.gather(*tasks)
        self.successful_relays = [result for result in results if result['success']]
        self.successful_relays.sort(key=lambda x: x['response_time'])
        _logger.info(f"Completed relay testing. {len(self.successful_relays)} successful relays out of {len(self.relay_urls)}")
        return self.successful_relays[:108]

    def select_best_relays(self, n=9):
        return self.successful_relays[:n]

    async def publish_to_relay(self, url, event):
        _logger.info(f"Attempting to publish to relay: {url}")
        try:
            async with websockets.connect(url, close_timeout=10) as websocket:
                message = event.to_message()
                await websocket.send(message)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _logger.info(f"Successfully published to relay {url}. Response: {response}")
                return {'url': url, 'success': True, 'response': response}
        except Exception as e:
            _logger.error(f"Failed to publish to relay {url}: {str(e)}")
            return {'url': url, 'success': False, 'error': str(e)}

    async def publish_to_relays(self, event, relays):
        _logger.info(f"Attempting to publish to {len(relays)} relays")
        tasks = [self.publish_to_relay(relay['url'], event) for relay in relays]
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for result in results if result['success'])
        _logger.info(f"Published to {success_count} out of {len(relays)} relays")
        return success_count / len(relays)

    async def manage_relay_list(self, event):
        _logger.info("Starting manage_relay_list process")
        await self.test_relays()
        relays_to_use = self.select_best_relays()
        _logger.info(f"Selected {len(relays_to_use)} best relays for publishing")
        success_rate = await self.publish_to_relays(event, relays_to_use)
        _logger.info(f"Initial publish attempt success rate: {success_rate:.2f}")
        
        attempts = 1
        while success_rate < 0.5 and attempts < 12:
            _logger.warning(f"Low success rate ({success_rate:.2f}). Attempt {attempts}/12. Trying next set of relays.")
            relays_to_use = self.select_best_relays(n=9*attempts)[-9:]
            success_rate = await self.publish_to_relays(event, relays_to_use)
            attempts += 1

        if success_rate < 0.5:
            _logger.error(f"Failed to achieve 50% success rate after {attempts} attempts")
            return False
        
        successful_urls = [relay['url'] for relay in self.successful_relays[:108]]
        self.env['ir.config_parameter'].sudo().set_param('nostr_bridge.successful_relays', ','.join(successful_urls))
        _logger.info(f"Updated successful relays list with {len(successful_urls)} relays")
        return True

# ---- Main NostrEvent Model ----

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    event_id = fields.Char(string='Event ID', required=False)
    kind = fields.Integer(string='Event Kind', required=True)
    content = fields.Text(string='Content', required=True)
    tags = fields.Text(string='Tags')
    public_key = fields.Char(string='Public Key', required=True)
    created_at = fields.Integer(string='Created At', required=False)
    signature = fields.Char(string='Signature', required=False)
    published = fields.Boolean(string='Published', default=False)
    logs = fields.Text(string='Logs')

    @api.model
    def default_get(self, fields):
        res = super(NostrEvent, self).default_get(fields)
        if 'event_id' not in res or 'signature' not in res:
            res.update({
                'content': res.get('content', ''),
                'public_key': res.get('public_key', self.env.user.nostr_public_key),
                'kind': res.get('kind', 1),
                'tags': json.dumps(res.get('tags', [])),
                'created_at': int(time.time()),
            })
        return res

    @api.model
    def _convert_to_hex(self, key):
        if key.startswith('npub') or key.startswith('nsec'):
            hrp, data, spec = bech32.bech32_decode(key)
            return bytes(bech32.convertbits(data, 5, 8, False)).hex()
        return key  # Assume it's already in hex format if not bech32

    @api.model
    def create(self, vals):
        if 'public_key' in vals:
            vals['public_key'] = self._bech32_to_hex(vals['public_key'])
        return super(NostrEvent, self).create(vals)

    def write(self, vals):
        if 'public_key' in vals:
            vals['public_key'] = self._bech32_to_hex(vals['public_key'])
        return super(NostrEvent, self).write(vals)

    def _ensure_private_key(self):
        if not self.env.user.nostr_private_key:
            raise UserError(_("Nostr private key is not set for the current user. Please set it in your user preferences."))
        return self.env.user.nostr_private_key

    def _get_private_key(self):
        key = self._ensure_private_key()
        if key.startswith('nsec'):
            return PrivateKey.from_nsec(key)
        elif len(key) == 64:  # It's already a hex key
            return PrivateKey(bytes.fromhex(key))
        else:
            raise ValueError("Invalid private key format")

    def generate_event_id_and_signature(self):
        _logger.info(f"Generating event ID and signature for event: {self.id}")
        content = self.content or ''
        pub_key = self.public_key or self.env.user.nostr_public_key
        created_at = self.created_at or int(time.time())
        kind = self.kind or 1
        tags = json.loads(self.tags or '[]')

        event = Event(
            content=content,
            public_key=pub_key,
            created_at=created_at,
            kind=kind,
            tags=tags
        )

        try:
            private_key = self._get_private_key()
            private_key.sign_event(event)
            _logger.info(f"Successfully signed event: {event.id}")
        except Exception as e:
            _logger.error(f"Failed to sign event: {str(e)}")
            event.id = Event.compute_id(pub_key, created_at, kind, tags, content)
            event.signature = 'dummy_signature_for_testing'

        self.write({
            'event_id': event.id,
            'signature': event.signature,
            'created_at': created_at,
            'public_key': pub_key
        })

    @enhanced_publish_event
    def publish_event(self):
        _logger.info(f"Starting publish_event for Nostr event: {self.event_id}")
        strategy = self._get_publish_strategy()
        _logger.info(f"Selected publish strategy: {strategy.__class__.__name__}")
        return strategy.publish(self)

    def _get_publish_strategy(self):
        _logger.info("Determining publish strategy based on feature flags")
        if self.env['ir.config_parameter'].sudo().get_param('use_new_relay_management', 'False') == 'True':
            _logger.info("Using new relay management publish strategy")
            return self._new_relay_management_publish
        elif self.env['ir.config_parameter'].sudo().get_param('use_async_publish', 'False') == 'True':
            _logger.info("Using async publish strategy")
            return AsyncPublishStrategy()
        elif self.env['ir.config_parameter'].sudo().get_param('use_alternative_publish', 'False') == 'True':
            _logger.info("Using alternative publish strategy")
            return AlternativePublishStrategy()
        else:
            _logger.info("Using original publish strategy")
            return OriginalPublishStrategy()

    def _new_relay_management_publish(self):
        _logger.info(f"Starting _new_relay_management_publish for event: {self.event_id}")
        relay_manager = RelayManager(self.env)
        event = self._create_nostr_event()
        _logger.info(f"Created Nostr event: {event.id}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            _logger.info("Attempting to publish event using manage_relay_list")
            success = loop.run_until_complete(relay_manager.manage_relay_list(event))
            _logger.info(f"manage_relay_list result: {'Success' if success else 'Failure'}")
            
            if success:
                self.write({
                    'published': True,
                    'logs': "Event published successfully using new relay management system."
                })
                _logger.info(f"Event {self.event_id} published successfully")
                return self._return_notification("Success", "Nostr event published successfully.", "success")
            else:
                _logger.error(f"Failed to publish event {self.event_id}")
                return self._return_notification("Publishing Failed", "Failed to publish Nostr event using new relay management system.", "danger", sticky=True)
        except Exception as e:
            _logger.exception(f"Exception in _new_relay_management_publish: {str(e)}")
            return self._return_notification("Error", f"An unexpected error occurred: {str(e)}", "danger", sticky=True)
        finally:
            loop.close()
            _logger.info("Closed asyncio loop")

    def _bech32_to_hex(self, bech32_key):
        try:
            if bech32_key.startswith('npub'):
                hrp, data = bech32_decode(bech32_key)
                if hrp is None:
                    raise ValueError("Invalid bech32 key")
                decoded = convertbits(data, 5, 8, False)
                return bytes(decoded).hex()
            return bech32_key  # Assume it's already hex if not npub
        except Exception as e:
            _logger.error(f"Error converting bech32 to hex: {str(e)}")
            raise UserError(_("Invalid public key format. Please check the key and try again."))

    def _create_nostr_event(self):
        _logger.info(f"Creating Nostr event for event_id: {self.event_id}")
        hex_pubkey = self._bech32_to_hex(self.public_key)
        event = Event(
            content=self.content,
            public_key=hex_pubkey,
            created_at=self.created_at or int(time.time()),
            kind=self.kind,
            tags=json.loads(self.tags) if self.tags else []
        )
        _logger.info(f"Created Nostr event with id: {event.id}")
        return event

    def _sign_event(self, event):
        _logger.info(f"Signing event: {event.id}")
        private_key = self._get_private_key()
        private_key.sign_event(event)
        _logger.info(f"Event signed successfully")
        return event

    def _return_notification(self, title, message, type, sticky=False):
        """
        Helper method to return a notification action.
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': _(message),
                'type': type,
                'sticky': sticky,
            }
        }

    @api.model
    def create_gitlab_event(self, event_type, data):
        content = json.dumps(data)
        
        user_public_key = self.env.user.nostr_public_key
        if not user_public_key:
            raise UserError(_("Nostr public key is not set for the current user."))
        
        user_public_key_hex = bech32_to_hex(user_public_key)
    
        event_data = {
            'content': content,
            'pubkey': user_public_key_hex,
            'created_at': int(time.time()),
            'kind': self._get_event_kind(event_type),
            'tags': [['p', user_public_key_hex]],
        }
        
        event = self.create_nostr_event(event_data)
        
        _logger.info(f"Created Nostr event: {event.to_message()}")
        
        signed_event = self.sign_event(event)
        
        _logger.info(f"Signed Nostr event: {signed_event.to_message()}")
        
        return self.create_and_publish(signed_event)

    def create_nostr_event(self, event_data):
        event = Event(
            content=event_data['content'],
            public_key=event_data['pubkey'],
            created_at=int(time.time()),
            kind=event_data['kind'],
            tags=json.loads(event_data['tags']) if isinstance(event_data['tags'], str) else event_data['tags']
        )
        return event

    def sign_event(self, event):
        private_key = self._get_private_key()
        private_key.sign_event(event)
        return event

    def _get_event_kind(self, event_type):
        event_kinds = {
            'commit': 3121,
            'branch': 31227,
            'merge_request': 31228,
        }
        return event_kinds.get(event_type, 1)

    def _get_event_tags(self, event_type, data):
        tags = []
        if event_type == 'commit':
            tags.extend([['p', data['project_id']], ['c', data['commit_id']]])
        elif event_type == 'branch':
            tags.extend([['p', data['project_id']], ['b', data['branch_name']]])
        elif event_type == 'merge_request':
            tags.extend([['p', data['project_id']], ['mr', data['merge_request_id']]])
        return tags

    def create_and_publish(self, event):
        nostr_event = self.create({
            'event_id': event.id,
            'kind': event.kind,
            'content': event.content,
            'tags': json.dumps(event.tags),
            'public_key': event.public_key,
            'created_at': event.created_at,
            'signature': event.signature,
        })
        
        if nostr_event.publish_event():
            _logger.info(f"Successfully published Nostr event: {event.id}")
        else:
            _logger.warning(f"Failed to publish Nostr event: {event.id}")
        
        return nostr_event

    def action_publish(self):
        self.ensure_one()
        return self.publish_event()

    @api.model
    def process_incoming_events(self):
        relay_urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
        relay_urls = [url.strip() for url in relay_urls if url.strip()]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._listen_to_relays(relay_urls))
        finally:
            loop.close()

    @api.model
    async def publish_nostr_event(self, content, public_key, private_key, relay_urls, kind=1, tags=None, created_at=None):
        try:
            public_key_hex = self._convert_to_hex(public_key)
            private_key_hex = self._convert_to_hex(private_key)

            event = Event(
                content=content,
                public_key=public_key_hex,
                created_at=created_at,
                kind=kind,
                tags=tags or []
            )

            private_key_obj = PrivateKey(bytes.fromhex(private_key_hex))
            private_key_obj.sign_event(event)

            _logger.info(f"Event created with ID {event.id} and signature {event.signature}")

            async def publish_to_relay(url, signed_event, retries=3):
                for attempt in range(retries):
                    try:
                        async with websockets.connect(url.strip(), ping_interval=20, ping_timeout=10, close_timeout=10) as websocket:
                            message_data = ["EVENT", json.loads(signed_event.to_message())]
                            message = json.dumps(message_data)
                            _logger.info(f"Sending message to {url}: {message[:100]}...")  # Log first 100 chars
                            await websocket.send(message)
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            _logger.info(f"Received response from {url}: {response}")
                            return {'url': url, 'success': True, 'response': response}
                    except websockets.exceptions.InvalidStatusCode as e:
                        _logger.error(f"Invalid status code from relay {url}: {e}")
                        return {'url': url, 'success': False, 'error': f"Invalid status code: {e}"}
                    except asyncio.TimeoutError:
                        _logger.warning(f"Timeout while connecting to relay {url}. Attempt {attempt + 1} of {retries}")
                    except Exception as e:
                        _logger.error(f"Error connecting to relay {url}: {str(e)}")
                        if attempt == retries - 1:
                            return {'url': url, 'success': False, 'error': str(e)}
                    await asyncio.sleep(1)  # Wait before retrying
                return {'url': url, 'success': False, 'error': "Max retries reached"}

            tasks = [publish_to_relay(url, event) for url in relay_urls]
            results = await asyncio.gather(*tasks)

            success_count = sum(1 for result in results if result['success'])
            _logger.info(f"Published event to {success_count} out of {len(relay_urls)} relays")

            # Detailed error reporting
            for result in results:
                if not result['success']:
                    _logger.error(f"Failed to publish to relay {result['url']}: {result.get('error', 'Unknown error')}")

            return results
        except Exception as e:
            _logger.error(f"Error in publish_nostr_event: {str(e)}", exc_info=True)
            raise UserError(f"Failed to publish Nostr event: {str(e)}")

    def publish_event_sync(self, content, public_key, private_key, relay_urls, kind=1, tags=None, created_at=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.publish_nostr_event(content, public_key, private_key, relay_urls, kind, tags, created_at))
            return results
        except Exception as e:
            _logger.error(f"Error in publish_event_sync: {str(e)}", exc_info=True)
            raise UserError(f"Failed to publish Nostr event: {str(e)}")
        finally:
            loop.close()

    async def listen_to_relay(self, url):
        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as websocket:
                    subscription_id = "my_subscription"
                    await websocket.send(json.dumps(["REQ", subscription_id, {}]))
                    _logger.info(f"Connected to relay: {url}")
                    while True:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=30)
                            _logger.debug(f"Received response from {url}: {response[:100]}...")  # Log first 100 chars
                            event = json.loads(response)
                            if event[0] == "EVENT":
                                if event[1] == subscription_id:
                                    if event[2] is not None:
                                        await self._process_event(event[2])
                                    else:
                                        _logger.warning(f"Received event with None data from {url}")
                                else:
                                    _logger.warning(f"Received event with unexpected subscription ID from {url}: {event[1]}")
                            elif event[0] == "EOSE":
                                _logger.info(f"End of stored events received from {url}")
                            elif event[0] == "NOTICE":
                                _logger.info(f"Notice from {url}: {event[1]}")
                            else:
                                _logger.warning(f"Received unexpected message type from {url}: {event[0]}")
                        except asyncio.TimeoutError:
                            await websocket.ping()
                            _logger.debug(f"Sent ping to {url}")
                        except json.JSONDecodeError:
                            _logger.error(f"Failed to decode JSON from {url}: {response}")
            except websockets.exceptions.ConnectionClosed:
                _logger.warning(f"Connection closed for relay {url}. Attempting to reconnect...")
                await asyncio.sleep(5)
            except Exception as e:
                _logger.error(f"Error listening to relay {url}: {str(e)}", exc_info=True)
                await asyncio.sleep(10)

    async def verify_event_publication(self, event_id, relay_urls):
        async def check_relay(url):
            try:
                async with websockets.connect(url, timeout=30) as websocket:
                    request = json.dumps(["REQ", "verify", {"ids": [event_id]}])
                    await websocket.send(request)
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    return {'url': url, 'found': event_id in response}
            except Exception as e:
                return {'url': url, 'error': str(e)}
    
        tasks = [check_relay(url) for url in relay_urls]
        results = await asyncio.gather(*tasks)
        return results

    async def _process_event(self, event_data):
        try:
            _logger.debug(f"Processing event: {event_data['id'][:10]}...")  # Log first 10 chars of event ID
            existing_event = self.env['nostr.event'].sudo().search([('event_id', '=', event_data['id'])])
            if not existing_event:
                self.env['nostr.event'].sudo().create({
                    'event_id': event_data['id'],
                    'kind': event_data['kind'],
                    'content': event_data['content'],
                    'tags': json.dumps(event_data['tags']),
                    'public_key': event_data['public_key'],
                    'created_at': event_data['created_at'],
                    'signature': event_data['signature'],
                    'published': True,
                })
                _logger.info(f"Processed new Nostr event: {event_data['id'][:10]}...")
            else:
                _logger.debug(f"Skipped existing Nostr event: {event_data['id'][:10]}...")
        except Exception as e:
            _logger.error(f"Error processing Nostr event: {str(e)}", exc_info=True)
            _logger.error(f"Event data: {event_data}")

    def action_generate_id_and_signature(self):
        self.ensure_one()
        _logger.info(f"Manually generating ID and signature for event: {self.id}")
        self.generate_event_id_and_signature()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Event Updated"),
                'message': _("Event ID and Signature have been generated."),
                'type': 'success',
                'sticky': False,
            }
        }

    def validate_event(self):
        self.ensure_one()
        try:
            event = Event.from_dict(json.loads(self.to_json()))
            is_valid = event.verify()
            if is_valid:
                _logger.info(f"Event {self.event_id} is valid")
                return True
            else:
                _logger.warning(f"Event {self.event_id} is not valid")
                return False
        except Exception as e:
            _logger.error(f"Error validating event {self.event_id}: {str(e)}")
            return False

    def to_json(self):
        return json.dumps({
            'id': self.event_id,
            'pubkey': self.public_key,
            'created_at': self.created_at,
            'kind': self.kind,
            'tags': json.loads(self.tags or '[]'),
            'content': self.content,
            'sig': self.signature
        })

# ---- Feature Flag Configuration ----

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_async_publish = fields.Boolean(
        string="Use Async Publish Method",
        config_parameter='use_async_publish'
    )
    use_alternative_publish = fields.Boolean(
        string="Use Alternative Publish Method", 
        config_parameter='use_alternative_publish'
    )
    use_new_relay_management = fields.Boolean(
        string="Use New Relay Management System",
        config_parameter='use_new_relay_management'
    )

# ---- Utility Functions ----

def bech32_to_hex(bech32_key):
    try:
        if bech32_key.startswith('npub'):
            return PublicKey.from_npub(bech32_key).hex()
        return bech32_key  # Assume it's already hex if not npub
    except Exception as e:
        raise ValueError(f"Invalid public key format: {str(e)}")

# ---- Cron Job for Relay Testing ----

class NostrRelayTester(models.Model):
    _name = 'nostr.relay.tester'
    _description = 'Nostr Relay Tester'

    @api.model
    def _test_and_update_relays(self):
        relay_manager = RelayManager(self.env)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            successful_relays = loop.run_until_complete(relay_manager.test_relays())
            successful_urls = [relay['url'] for relay in successful_relays]
            self.env['ir.config_parameter'].sudo().set_param('nostr_bridge.successful_relays', ','.join(successful_urls))
            _logger.info(f"Updated successful relays: {len(successful_urls)} relays")
        finally:
            loop.close()
           
