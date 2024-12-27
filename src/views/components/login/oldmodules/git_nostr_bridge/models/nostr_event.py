import asyncio
import json
import logging
import websockets
from urllib.parse import urlparse
import time
import traceback

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.event import Event as NostrLibEvent
from nostr.key import PrivateKey

_logger = logging.getLogger(__name__)

class NostrEvent(models.Model):
    _name = 'nostr.event'
    _description = 'Nostr Event'

    name = fields.Char(string='Name', required=True)
    event_type = fields.Selection([
        ('repo_anchor', 'Repository Anchor'),
        ('branch', 'Branch'),
        ('commit', 'Commit'),
        ('tree', 'Tree'),
        ('blob', 'Blob'),
    ], string='Event Type', required=True)
    content = fields.Text(string='Content')
    tags = fields.Text(string='Tags')
    published = fields.Boolean(string='Published', default=False)
    event_id = fields.Char(string='Event ID', readonly=True)
    kind = fields.Integer(string='Nostr Event Kind', default=1)

    @api.model
    def action_publish(self, event_id):
        event = self.browse(event_id)
        _logger.info(f"Starting publish action for event: {event.name}")
        start_time = time.time()

        try:
            if not self.env.user.nostr_private_key:
                raise UserError(_("Nostr private key is not set for the current user."))

            _logger.info("Generating private key")
            try:
                private_key = PrivateKey.from_nsec(self.env.user.nostr_private_key)
                _logger.info("Private key generated successfully")
            except Exception as e:
                _logger.error(f"Failed to generate private key: {str(e)}")
                _logger.error(traceback.format_exc())
                raise UserError(_("Invalid Nostr private key: %s") % str(e))

            public_key = private_key.public_key.hex()
            _logger.info(f"Public key: {public_key}")

            _logger.info("Parsing tags")
            try:
                tags = json.loads(event.tags) if event.tags else []
                _logger.info(f"Parsed tags: {tags}")
                if not isinstance(tags, list):
                    raise ValueError("Tags must be a list of lists")
                for tag in tags:
                    if not isinstance(tag, list):
                        raise ValueError("Each tag must be a list")
            except json.JSONDecodeError as e:
                _logger.error(f"JSON decode error: {str(e)}")
                _logger.error(traceback.format_exc())
                raise UserError(_("Invalid tags format. Please ensure tags are in valid JSON format."))
            except ValueError as e:
                _logger.error(f"Value error: {str(e)}")
                _logger.error(traceback.format_exc())
                raise UserError(_("Invalid tags format: %s") % str(e))

            _logger.info("Creating Nostr event")
            nostr_event = NostrLibEvent(
                kind=1,  # Assuming TEXT_NOTE, adjust if needed
                content=str(event.content),
                tags=tags,
                public_key=public_key  # Ensure public_key is provided
            )
            private_key.sign_event(nostr_event)
            _logger.info(f"Event created: {nostr_event.to_message()}")

            _logger.info("Fetching relay URLs")
            relay_urls = self.env['ir.config_parameter'].sudo().get_param('git_nostr_bridge.relay_urls', '').split(',')
            relay_urls = [url.strip() for url in relay_urls if url.strip()][:5]  # Limit to 5 relays
            _logger.info(f"Relay URLs: {relay_urls}")

            if not relay_urls:
                raise UserError(_("No Nostr relay URLs configured. Please set them in the settings."))

            _logger.info("Validating relay URLs")
            for url in relay_urls:
                parsed = urlparse(url)
                if parsed.scheme not in ('ws', 'wss'):
                    _logger.error(f"Invalid relay URL: {url}")
                    raise UserError(_("Invalid relay URL: %s. Must start with ws:// or wss://") % url)

            async def publish_to_relay(relay_url, nostr_event, retries=3):
                for attempt in range(retries):
                    try:
                        _logger.info(f"Attempting to connect to {relay_url} (attempt {attempt + 1})")
                        connection_start = time.time()
                        async with websockets.connect(relay_url, timeout=30) as websocket:
                            connection_end = time.time()
                            _logger.info(f"Connected to {relay_url} in {connection_end - connection_start:.2f} seconds")
                            
                            message = nostr_event.to_message()
                            _logger.debug(f"Raw event message: {message}")
                            
                            # The message is already in the correct format, so we don't need to modify it
                            _logger.info(f"Sending Nostr event to {relay_url}: {message}")
                            
                            send_start = time.time()
                            await websocket.send(message)
                            send_end = time.time()
                            _logger.info(f"Sent message to {relay_url} in {send_end - send_start:.2f} seconds")
                            
                            _logger.info(f"Waiting for response from {relay_url}")
                            response_start = time.time()
                            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                            response_end = time.time()
                            _logger.info(f"Received response from {relay_url} in {response_end - response_start:.2f} seconds: {response}")
                            
                            try:
                                return json.loads(response)
                            except json.JSONDecodeError as e:
                                _logger.error(f"Failed to parse response from {relay_url}: {str(e)}")
                                return f"Invalid response from {relay_url}: {response}"
                    except (websockets.exceptions.WebSocketException, asyncio.TimeoutError) as e:
                        _logger.error(f"Error publishing to {relay_url} (attempt {attempt + 1}): {str(e)}")
                        _logger.error(traceback.format_exc())
                        await asyncio.sleep(5 * (attempt + 1))  # Increased delay between attempts
                return f"Failed to publish to {relay_url} after {retries} attempts"

            async def publish_with_timeout():
                tasks = [publish_to_relay(url, nostr_event) for url in relay_urls]
                return await asyncio.gather(*tasks, return_exceptions=True)

            async def run_publication():
                _logger.info("Starting publication process")
                try:
                    results = await asyncio.wait_for(publish_with_timeout(), timeout=120)  # Increased overall timeout
                    _logger.info(f"Publication results: {results}")
                    return results
                except asyncio.TimeoutError:
                    _logger.error("Publication process timed out after 120 seconds")
                    raise UserError(_("Publishing timed out after 120 seconds"))

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(run_publication())
            finally:
                loop.close()

            success = any(isinstance(result, list) and result[0] == "OK" for result in results)
            if success:
                event.write({
                    'published': True,
                    'event_id': nostr_event.id
                })
                _logger.info(f"Successfully published Nostr event: {nostr_event.id}")
                
                # Verify event publication
                self.verify_event_publication(nostr_event.id, relay_urls)
                
                end_time = time.time()
                _logger.info(f"Total publish action time: {end_time - start_time:.2f} seconds")
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _("Nostr event successfully published to at least one relay."),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                error_messages = [str(result) for result in results if isinstance(result, str)]
                _logger.error(f"Failed to publish Nostr event: {'; '.join(error_messages)}")
                raise UserError(_("Failed to publish Nostr event: %s") % "; ".join(error_messages))

        except Exception as e:
            _logger.error(f"Unexpected error in action_publish: {str(e)}")
            _logger.error(traceback.format_exc())
            raise UserError(_("An unexpected error occurred: %s") % str(e))

    @api.model
    def verify_event_publication(self, event_id, relay_urls, max_attempts=5, delay=2):
        _logger.info(f"Starting verification for event: {event_id}")
        for attempt in range(max_attempts):
            _logger.info(f"Verification attempt {attempt + 1}")
            for url in relay_urls:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.query_event(url, event_id))
                    if result:
                        _logger.info(f"Event {event_id} found on relay {url}")
                        return True
                except Exception as e:
                    _logger.error(f"Error querying event from {url}: {str(e)}")
                    _logger.error(traceback.format_exc())
                finally:
                    loop.close()
            _logger.info(f"Waiting {delay} seconds before next attempt")
            time.sleep(delay)
        _logger.warning(f"Event {event_id} not found on any relay after {max_attempts} attempts")
        return False

    async def query_event(self, relay_url, event_id):
        _logger.info(f"Querying event {event_id} from {relay_url}")
        start_time = time.time()
        try:
            async with websockets.connect(relay_url, timeout=10) as websocket:
                request = json.dumps(["REQ", "query", {"ids": [event_id]}])
                _logger.info(f"Sending query to {relay_url}: {request}")
                await websocket.send(request)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _logger.info(f"Response from {relay_url}: {response}")
                end_time = time.time()
                _logger.info(f"Query to {relay_url} took {end_time - start_time:.2f} seconds")
                return json.loads(response)
        except Exception as e:
            _logger.error(f"Error querying {relay_url}: {str(e)}")
            _logger.error(traceback.format_exc())
            end_time = time.time()
            _logger.info(f"Failed query to {relay_url} took {end_time - start_time:.2f} seconds")
            return None
