# utils/nostr_websocket_client.py
import logging
import time
import websocket
import json

_logger = logging.getLogger(__name__)

class NostrWebSocketClient:
    def __init__(self, relay_urls):
        self.relay_urls = relay_urls

    def connect_and_publish(self, event_data):
        responses = []
        logs = []
        for url in self.relay_urls:
            try:
                response, log = self._connect_and_publish_to_relay(url, event_data)
                responses.append(response)
                logs.extend(log)
            except Exception as e:
                error_message = f"Error publishing event to relay {url}: {e}"
                _logger.error(error_message)
                logs.append(error_message)
        return responses, logs

    def _connect_and_publish_to_relay(self, relay_url, event_data):
        log = []
        log.append(f"Attempting to connect to {relay_url}")
        start_time = time.time()

        ws = websocket.create_connection(relay_url)
        log.append(f"Connected to {relay_url} in {time.time() - start_time:.2f} seconds")

        event_message = json.dumps(["EVENT", event_data])
        log.append(f"Sending Nostr event to {relay_url}")
        ws.send(event_message)
        log.append(f"Sent message to {relay_url} in {time.time() - start_time:.2f} seconds")

        log.append(f"Waiting for response from {relay_url}")
        response = ws.recv()
        log.append(f"Received response from {relay_url} in {time.time() - start_time:.2f} seconds: {response}")
        ws.close()
        return json.loads(response), log
