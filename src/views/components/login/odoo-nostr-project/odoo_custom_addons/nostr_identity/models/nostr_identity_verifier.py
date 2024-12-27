from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json
import websocket
import threading
import ssl
import time
from odoo.tools import config

_logger = logging.getLogger(__name__)

class NostrIdentityVerifier(models.Model):
    _name = 'nostr.identity.verifier'
    _description = 'Nostr Identity Verifier'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    relay_url = fields.Char(string='Relay URL', required=True)
    websocket_state = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connecting', 'Connecting'),
        ('connected', 'Connected')
    ], default='disconnected', string='WebSocket State', readonly=True)
    last_error = fields.Text(string='Last Error', readonly=True)

    def _get_ws_connection(self):
        return self.env.context.get('ws_connection')

    def _set_ws_connection(self, ws):
        self = self.with_context(ws_connection=ws)

    def connect_to_relay(self):
        self.ensure_one()
        if self.websocket_state == 'connected':
            return True

        self.websocket_state = 'connecting'
        self.last_error = False

        try:
            ws = self._create_websocket(self.relay_url)
            self._set_ws_connection(ws)
            
            # Wait for connection to establish or fail
            for _ in range(20):  # Wait up to 10 seconds
                if self.websocket_state == 'connected':
                    return True
                elif self.websocket_state == 'disconnected':
                    raise UserError(self.last_error or _("Connection failed"))
                time.sleep(0.5)

            raise UserError(_("Connection timeout"))
        except Exception as e:
            self.websocket_state = 'disconnected'
            self.last_error = str(e)
            _logger.error(f"Failed to connect to {self.relay_url}: {str(e)}")
            return False

    def _create_websocket(self, relay_url):
        def on_message(ws, message):
            with self.pool.cursor() as new_cr:
                self.with_env(self.env(cr=new_cr))._handle_message(message)

        def on_error(ws, error):
            with self.pool.cursor() as new_cr:
                self.with_env(self.env(cr=new_cr))._handle_error(error)

        def on_close(ws, close_status_code, close_msg):
            with self.pool.cursor() as new_cr:
                self.with_env(self.env(cr=new_cr))._handle_close()

        def on_open(ws):
            with self.pool.cursor() as new_cr:
                self.with_env(self.env(cr=new_cr))._handle_open()

        ws = websocket.WebSocketApp(relay_url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open)

        wst = threading.Thread(target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}))
        wst.daemon = True
        wst.start()

        return ws

    def _handle_message(self, message):
        _logger.info(f"Received message from {self.relay_url}: {message}")
        self.env['nostr.message'].create({
            'verifier_id': self.id,
            'content': message
        })

    def _handle_error(self, error):
        _logger.error(f"WebSocket error for {self.relay_url}: {error}")
        self.write({'last_error': str(error), 'websocket_state': 'disconnected'})

    def _handle_close(self):
        _logger.info(f"WebSocket connection closed for {self.relay_url}")
        self.write({'websocket_state': 'disconnected'})

    def _handle_open(self):
        _logger.info(f"WebSocket connection opened for {self.relay_url}")
        self.write({'websocket_state': 'connected'})

    def publish_event(self, event):
        self.ensure_one()
        if self.websocket_state != 'connected':
            if not self.connect_to_relay():
                raise UserError(_("Failed to connect to relay"))

        try:
            message = json.dumps(["EVENT", event])
            ws = self._get_ws_connection()
            if ws:
                ws.send(message)
                _logger.info(f"Published event to {self.relay_url}")
                return True
            else:
                raise UserError(_("WebSocket connection is not available"))
        except Exception as e:
            _logger.error(f"Failed to publish event to {self.relay_url}: {str(e)}")
            raise UserError(_("Failed to publish event: %s") % str(e))

    @api.model
    def process_messages(self):
        messages = self.env['nostr.message'].search([('processed', '=', False)])
        for message in messages:
            try:
                # Process the message here
                _logger.info(f"Processing message: {message.content}")
                # Add your message processing logic here
                message.write({'processed': True})
            except Exception as e:
                _logger.error(f"Error processing message {message.id}: {str(e)}")

    def close_connection(self):
        self.ensure_one()
        ws = self._get_ws_connection()
        if ws:
            try:
                ws.close()
            except Exception as e:
                _logger.error(f"Error closing WebSocket for {self.relay_url}: {str(e)}")
        self._set_ws_connection(None)
        self.write({'websocket_state': 'disconnected'})
