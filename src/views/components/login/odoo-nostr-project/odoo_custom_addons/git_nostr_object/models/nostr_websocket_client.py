import websocket
import json
import logging
import time

_logger = logging.getLogger(__name__)

class NostrWebSocketClient:
    def __init__(self, relay_urls):
        self.relay_urls = relay_urls

    def connect_and_publish(self, event_data):
        responses = []
        for url in self.relay_urls:
            try:
                _logger.info(f"Attempting to connect to {url}")
                start_time = time.time()
                ws = websocket.create_connection(url, timeout=10)
                _logger.info(f"Connected to {url} in {time.time() - start_time:.2f} seconds")

                # Construct the message correctly
                message = ["EVENT", event_data]
                _logger.debug(f"Raw event message: {message}")

                ws.send(json.dumps(message))
                _logger.info(f"Sent message to {url} in {time.time() - start_time:.2f} seconds")

                _logger.info(f"Waiting for response from {url}")
                response = ws.recv()
                _logger.info(f"Received response from {url} in {time.time() - start_time:.2f} seconds: {response}")

                responses.append(json.loads(response))
                ws.close()
            except Exception as e:
                _logger.error(f"Error publishing to {url}: {str(e)}")
                responses.append(["ERROR", str(e)])
        return responses
