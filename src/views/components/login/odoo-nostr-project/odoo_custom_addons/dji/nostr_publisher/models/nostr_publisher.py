from hashlib import sha256
from secp256k1 import PublicKey as Secp256k1PublicKey, PrivateKey as Secp256k1PrivateKey
import json
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.event import Event, EventKind
from nostr.key import PrivateKey
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
import secrets
import logging
import asyncio
import websockets
from odoo.addons.queue_job import Job
from .nostr_event import NostrEvent
from nostr.bech32 import bech32_decode, convertbits

_logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2

class NostrPublisher(models.Model):
    _name = 'nostr.publisher'
    _description = 'Nostr Publisher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='draft', tracking=True)
    public_key = fields.Char(string='Public Key', compute='_compute_keys', store=True)
    private_key = fields.Char(string='Private Key', compute='_compute_keys', store=True)
    relay_count = fields.Integer(string='Number of Relays', compute='_compute_relay_count')
    last_publish_date = fields.Datetime(string='Last Publish Date')
    total_events_published = fields.Integer(string='Total Events Published', default=0)
    success_count = fields.Integer(string='Successful Publishes', default=0)
    success_rate = fields.Float(string='Success Rate', compute='_compute_success_rate')
    
    relay_ids = fields.One2many('nostr.relay', 'publisher_id', string='Relays')
    connected_module_ids = fields.One2many('nostr.connected.module', 'publisher_id', string='Connected Modules')
    active_relay_ids = fields.Many2many('nostr.relay', string='Active Relays', compute='_compute_active_relays', store=True)

    @api.depends('create_date', 'write_date')
    def _compute_keys(self):
        for record in self:
            user = self.env.user
            if user.nostr_public_key and user.nostr_private_key:
                record.public_key = user.nostr_public_key
                record.private_key = user.nostr_private_key
                _logger.info(f"Keys set for user {user.name}: Public key: {record.public_key[:10]}..., Private key: {record.private_key[:10]}...")
            else:
                record.public_key = False
                record.private_key = False
                _logger.warning(f"Nostr keys not set for user {user.name}")

    @api.depends('relay_ids', 'relay_ids.is_active')
    def _compute_active_relays(self):
        for record in self:
            active_relays = record.relay_ids.filtered(lambda r: r.is_active)
            record.active_relay_ids = active_relays[:9]  # Limit to top 9 active relays

    @api.depends('relay_ids')
    def _compute_relay_count(self):
        for record in self:
            record.relay_count = len(record.relay_ids)

    @api.depends('total_events_published', 'success_count')
    def _compute_success_rate(self):
        for record in self:
            if record.total_events_published > 0:
                record.success_rate = (record.success_count / record.total_events_published) * 100
            else:
                record.success_rate = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'public_key' not in vals or 'private_key' not in vals:
                private_key, public_key = self._generate_key_pair()
                vals['public_key'] = public_key
                vals['private_key'] = private_key
        return super(NostrPublisher, self).create(vals_list)

    def _generate_key_pair(self):
        try:
            private_key = PrivateKey()
            public_key = private_key.public_key
            return private_key.bech32(), private_key.public_key.bech32()
        except Exception as e:
            _logger.error(f"Error generating Nostr key pair: {str(e)}")
            raise UserError(_("Failed to generate Nostr key pair. Please try again."))

    def test_relay_connections(self):
        self.ensure_one()
        for relay in self.relay_ids:
            is_active, response_time = self._test_relay_connection(relay.url)
            relay.write({
                'is_active': is_active,
                'last_connection': fields.Datetime.now() if is_active else relay.last_connection,
                'connection_failures': 0 if is_active else relay.connection_failures + 1,
                'response_time': response_time,
            })
        self._compute_active_relays()
        self.env.cr.commit()

    @api.model
    def cron_test_relay_connections(self):
        publishers = self.search([('state', '=', 'active')])
        for publisher in publishers:
            publisher.test_relay_connections()

    @api.model
    def publish_event(self, content, kind=1, tags=None):
        _logger.info(f"Starting publish_event - Content: {content[:50]}, Kind: {kind}, Tags: {tags}")
        self.ensure_one()
        if self.state != 'active':
            _logger.warning("Nostr Publisher is not active.")
            raise UserError(_("Nostr Publisher is not active."))
    
        if not self.private_key or not self.public_key:
            _logger.error("Nostr keys are not set.")
            raise UserError(_("Nostr keys are not set. Please check your configuration."))
    
        _logger.info(f"Preparing event data")
        try:
            event_data = {
                'kind': kind,
                'content': content,
                'tags': tags or [],
                'public_key': self._convert_to_hex(self.public_key),
            }
            _logger.info(f"Event data prepared: {event_data}")
    
            # Create and sign the event
            private_key = PrivateKey.from_nsec(self.private_key)
            event = Event(
                content=event_data['content'],
                public_key=event_data['public_key'],
                created_at=int(time.time()),
                kind=event_data['kind'],
                tags=event_data['tags']
            )
            private_key.sign_event(event)
            _logger.info(f"Event created and signed with ID: {event.id}")
    
            # Get relay URLs
            relay_urls = self._get_relay_urls()
            if not relay_urls:
                raise UserError(_("No active relay URLs configured"))
    
            # Publish to relays
            success_count = 0
            for url in relay_urls:
                try:
                    success = self._publish_to_single_relay(url, event)
                    if success:
                        success_count += 1
                except Exception as e:
                    _logger.error(f"Failed to publish to relay {url}: {str(e)}")
    
            if success_count > 0:
                self.total_events_published += 1
                self.success_count += 1
                self.last_publish_date = fields.Datetime.now()
                _logger.info(f"Event published successfully to {success_count} out of {len(relay_urls)} relays. Total events: {self.total_events_published}")
                return True
            else:
                _logger.error(f"Failed to publish event to any relay")
                raise UserError(_("Failed to publish event to any relay. Please check relay connections and try again later."))
        except Exception as e:
            _logger.exception(f"Unexpected error in publish_event: {str(e)}")
            raise UserError(_("An unexpected error occurred while publishing the event: %s") % str(e))
    
    def _get_relay_urls(self):
        return self.active_relay_ids.mapped('url')
    
    def _publish_to_single_relay(self, url, event):
        try:
            _logger.info(f"Attempting to publish to relay: {url}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self._async_publish_to_relay(url, event))
            loop.close()
            return success
        except Exception as e:
            _logger.error(f"Error publishing to relay {url}: {str(e)}")
            return False
    
    async def _async_publish_to_relay(self, url, event):
        try:
            async with websockets.connect(url.strip(), ping_interval=20, ping_timeout=10, close_timeout=10) as websocket:
                message = event.to_message()
                _logger.info(f"Sending message to {url}: {message[:100]}...")
                await websocket.send(message)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _logger.info(f"Received response from {url}: {response}")
                return json.loads(response)[0] == "OK"
        except Exception as e:
            _logger.error(f"Error in _async_publish_to_relay for {url}: {str(e)}")
            return False
        
    def _create_nostr_event(self, content, kind, tags):
        return Event(
            content=content,
            public_key=self._convert_to_hex(self.public_key),
            created_at=int(time.time()),
            kind=kind,
            tags=tags or []
        )

    @api.model
    def _convert_to_hex(self, key):
        if key.startswith('npub') or key.startswith('nsec'):
            try:
                decoded = bech32_decode(key)
                if decoded is None or len(decoded) != 3:
                    raise ValueError(f"Invalid bech32 key: {key}")
                hrp, data, spec = decoded
                if data is None:
                    raise ValueError(f"Invalid bech32 key data: {key}")
                converted = convertbits(data, 5, 8, False)
                if converted is None:
                    raise ValueError(f"Failed to convert bech32 key: {key}")
                return bytes(converted).hex()
            except Exception as e:
                _logger.error(f"Error converting bech32 to hex: {str(e)}")
                raise ValueError(f"Failed to convert bech32 key: {key}") from e
        return key  # Assume it's already in hex format if not bech32

    def _sign_event(self, event):
        private_key = PrivateKey.from_nsec(self.private_key)
        private_key.sign_event(event)
        return event

    def _publish_to_relays(self, event, relay_urls):
        results = []
        for url in relay_urls:
            try:
                response = self._sync_websocket_request(url, event.to_message())
                _logger.info(f"Raw response from relay {url}: {response}")
                success = json.loads(response)[0] == "OK" if response else False
                results.append({'url': url, 'success': success, 'response': response})
            except Exception as e:
                _logger.error(f"Failed to publish to relay {url}: {str(e)}")
                results.append({'url': url, 'success': False, 'error': str(e)})
        
        success = any(result['success'] for result in results)
        _logger.info(f"Publication results: {results}")
        return success, results

    def _sync_websocket_request(self, url, message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_websocket_request(url, message))
        finally:
            loop.close()

    async def _async_websocket_request(self, url, message):
        try:
            async with websockets.connect(url.strip(), ping_interval=20, ping_timeout=10, close_timeout=10) as websocket:
                _logger.info(f"Sending message to {url}: {message[:100]}...")
                await websocket.send(message)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _logger.info(f"Received response from {url}: {response}")
                return response
        except websockets.exceptions.ConnectionClosed:
            _logger.error(f"Connection closed for {url} before sending message")
            return None
        except asyncio.TimeoutError:
            _logger.error(f"Timeout while connecting to {url}")
            return None
        except Exception as e:
            _logger.error(f"Error in _async_websocket_request for {url}: {str(e)}")
            return None
    
    def _verify_event_published(self, event_id, relay_urls, max_attempts=3, delay_between_attempts=2):
        _logger.info(f"Verifying publication of event {event_id}")
    
        for attempt in range(max_attempts):
            _logger.info(f"Verification attempt {attempt + 1} of {max_attempts}")
    
            for url in relay_urls:
                try:
                    event_found = self._sync_verify_request(url, event_id)
                    if event_found:
                        _logger.info(f"Event {event_id} found on relay {url}")
                        return True
                except Exception as e:
                    _logger.warning(f"Error checking relay {url}: {str(e)}")
    
            if attempt < max_attempts - 1:
                _logger.info(f"Event not found. Waiting {delay_between_attempts} seconds before next attempt...")
                time.sleep(delay_between_attempts)
    
        _logger.warning(f"Failed to verify event {event_id} on any relay after {max_attempts} attempts")
        return False
    
    def _sync_verify_request(self, url, event_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_verify_request(url, event_id))
        finally:
            loop.close()

    async def _async_verify_request(self, url, event_id):
        try:
            async with websockets.connect(url.strip(), ping_interval=20, ping_timeout=10, close_timeout=10) as websocket:
                request = json.dumps(["REQ", "verify", {"ids": [event_id]}])
                await websocket.send(request)
                for _ in range(3):  # Wait for up to 3 messages
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    if response.startswith('["EVENT"'):
                        event_data = json.loads(response)[2]
                        if event_data.get('id') == event_id:
                            _logger.info(f"Event {event_id} found on relay {url}")
                            return True
                    elif response == '["EOSE","verify"]':
                        break
            return False
        except Exception as e:
            _logger.error(f"Error in _async_verify_request for {url}: {str(e)}")
            return False
    
    def _test_relay_connection(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                is_active, response_time = self._sync_test_relay_connection(url)
                if is_active:
                    return is_active, response_time
                _logger.warning(f"Failed to connect to relay {url}. Attempt {attempt + 1} of {max_retries}")
            except Exception as e:
                _logger.error(f"Error testing connection to {url}: {str(e)}")
            time.sleep(1)  # Wait before retrying
        return False, 0

    def _sync_test_relay_connection(self, url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_test_relay_connection(url))
        finally:
            loop.close()

    async def _async_test_relay_connection(self, url):
        try:
            _logger.info(f"Testing connection to relay: {url}")
            start_time = time.time()
            async with websockets.connect(url.strip(), ping_interval=None) as websocket:
                # Create a test event
                private_key = PrivateKey()
                pub_key = private_key.public_key.hex()
                event = Event(
                    public_key=pub_key,
                    created_at=int(time.time()),
                    kind=1,
                    tags=[],
                    content="Test connection from Odoo"
                )
                private_key.sign_event(event)
                
                message = event.to_message()
                await websocket.send(message)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _logger.info(f"Received response from {url}: {response}")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                return json.loads(response)[0] == "OK", response_time
        except Exception as e:
            _logger.error(f"Error testing connection to {url}: {str(e)}")
            return False, 0

    @api.model
    def publish_event_for_module(self, module_name, event_type, content, tags=None):
        active_publisher = self.search([('state', '=', 'active')], limit=1)
        if not active_publisher:
            raise UserError(_("No active Nostr Publisher configured"))

        event_content = json.dumps({
            'module': module_name,
            'type': event_type,
            'content': content
        })
        
        if tags is None:
            tags = []
        tags.append(['e', module_name])
        tags.append(['t', event_type])

        _logger.info(f"Publishing event for module: {module_name}, type: {event_type}")
        return active_publisher.publish_event(event_content, kind=1, tags=tags)

    def listen_for_events(self):
        _logger.info("Starting listen_for_events")
        job = Job(func=self._listen_for_events)
        job.set_channel("root.nostr")
        job.store()
        _logger.info("listen_for_events job stored")
        return job

    def _listen_for_events(self):
        _logger.info("Starting _listen_for_events")
        async def listen_to_relay(url):
            while True:
                try:
                    _logger.info(f"Attempting to connect to relay: {url}")
                    async with websockets.connect(url.strip(), ping_interval=20, ping_timeout=10) as websocket:
                        await websocket.send(json.dumps(["REQ", "listen_job", {"kinds": [1]}]))
                        _logger.info(f"Connected to relay: {url}")
                        while True:
                            try:
                                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                                _logger.debug(f"Received response from {url}: {response[:100]}...")
                                event = json.loads(response)
                                if event[0] == "EVENT":
                                    await self._process_event(event[2])
                                elif event[0] == "EOSE":
                                    _logger.info(f"End of stored events received from {url}")
                                elif event[0] == "NOTICE":
                                    _logger.info(f"Notice from {url}: {event[1]}")
                                else:
                                    _logger.warning(f"Received unexpected message type from {url}: {event[0]}")
                            except asyncio.TimeoutError:
                                await websocket.ping()
                                _logger.debug(f"Sent ping to {url}")
                except websockets.exceptions.ConnectionClosed:
                    _logger.warning(f"Connection closed for relay {url}. Attempting to reconnect...")
                    await asyncio.sleep(5)
                except Exception as e:
                    _logger.error(f"Error listening to relay {url}: {str(e)}", exc_info=True)
                    await asyncio.sleep(10)

        relay_urls = self.active_relay_ids.mapped('url')
        if not relay_urls:
            _logger.error("No active relay URLs configured")
            raise UserError(_("No active relay URLs configured"))

        async def listen_to_all_relays():
            _logger.info(f"Starting to listen to {len(relay_urls)} relays")
            tasks = [listen_to_relay(url) for url in relay_urls]
            await asyncio.gather(*tasks)

        _logger.info("Running listen_to_all_relays")
        asyncio.run(listen_to_all_relays())

    @api.model
    def start_listening(self):
        _logger.info("Starting start_listening method")
        jobs = self.env['queue.job'].search([
            ('method_name', '=', '_listen_for_events'),
            ('state', 'in', ['pending', 'enqueued', 'started'])
        ])
        if not jobs:
            _logger.info("No existing _listen_for_events jobs found, creating new job")
            self.listen_for_events()
        else:
            _logger.info(f"Found {len(jobs)} existing _listen_for_events jobs")

    async def _process_event(self, event_data):
        try:
            _logger.debug(f"Processing event: {event_data['id'][:10]}...")
            existing_event = self.env['nostr.event'].sudo().search([('event_id', '=', event_data['id'])])
            if not existing_event:
                self.env['nostr.event'].sudo().create({
                    'event_id': event_data['id'],
                    'kind': event_data['kind'],
                    'content': event_data['content'],
                    'tags': json.dumps(event_data['tags']),
                    'public_key': event_data['pubkey'],
                    'created_at': event_data['created_at'],
                    'signature': event_data['sig'],
                    'published': True,
                })
                _logger.info(f"Processed new Nostr event: {event_data['id'][:10]}...")
            else:
                _logger.debug(f"Skipped existing Nostr event: {event_data['id'][:10]}...")
        except Exception as e:
            _logger.error(f"Error processing Nostr event: {str(e)}", exc_info=True)
            _logger.error(f"Event data: {event_data}")

    @api.model
    def dispatch_event(self, event):
        try:
            _logger.info(f"Dispatching event: {event['id'][:10]}...")
            content = json.loads(event['content'])
            module = content.get('module')
            event_type = content.get('type')

            if module and event_type:
                method_name = f'handle_nostr_event_{event_type}'
                model = self.env[f'{module}.nostr_handler']
                if hasattr(model, method_name):
                    _logger.info(f"Calling handler method: {method_name} for module: {module}")
                    getattr(model, method_name)(content['content'])
                else:
                    _logger.warning(f"No handler found for event type {event_type} in module {module}")
            else:
                _logger.warning(f"Invalid event content structure: {content}")
        except Exception as e:
            _logger.error(f"Error dispatching event: {str(e)}", exc_info=True)

    def action_submit_event(self):
        self.ensure_one()
        _logger.info(f"Opening submit event wizard for publisher: {self.name}")
        return {
            'name': _('Submit Nostr Event'),
            'type': 'ir.actions.act_window',
            'res_model': 'submit.event.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_publisher_id': self.id},
        }

    def update_active_relays(self):
        self.ensure_one()
        _logger.info(f"Updating active relays for publisher: {self.name}")
        self.test_relay_connections()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Active Relays Updated"),
                'message': _("The active relays have been updated based on their current status."),
                'sticky': False,
            }
        }

    @api.model
    def cron_update_active_relays(self):
        _logger.info("Starting cron job to update active relays")
        publishers = self.search([('state', '=', 'active')])
        for publisher in publishers:
            _logger.info(f"Updating active relays for publisher: {publisher.name}")
            publisher.update_active_relays()

    def action_test_relays(self):
        self.ensure_one()
        _logger.info(f"Testing relays for publisher: {self.name}")
        self.test_relay_connections()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Relay Test Completed"),
                'message': _("All relays have been tested. Check the relay list for updated statuses."),
                'sticky': False,
            }
        }
