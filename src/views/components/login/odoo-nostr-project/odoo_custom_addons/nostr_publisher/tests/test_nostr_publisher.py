from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
import json
from odoo.exceptions import UserError

class TestNostrPublisher(TransactionCase):

    def setUp(self):
        super(TestNostrPublisher, self).setUp()
        self.NostrPublisher = self.env['nostr.publisher']
        self.publisher = self.NostrPublisher.create({
            'name': 'Test Publisher',
            'state': 'active',
            'public_key': 'npub1k67zuuskqjj6le8ychjxh7c9tkkkpc54ap25unr88thucpl3hg7skj8cwj',
            'private_key': 'nsec1x5th4f546z9kgxnapudzpc5u68p9c70gh95xd7ls2y6lhvg8jg4sxwyaq3'
        })
        self.relay = self.env['nostr.relay'].create({
            'publisher_id': self.publisher.id,
            'url': 'wss://relay.damus.io'
        })

    def test_create_event(self):
        event = self.publisher.create_event("Test content")
        self.assertEqual(event['content'], "Test content")
        self.assertEqual(event['public_key'], self.publisher.public_key)
        self.assertIn('id', event)
        self.assertIn('signature', event)

    @patch('odoo.addons.nostr_publisher.models.nostr_publisher.asyncio.run')
    def test_publish_event(self, mock_asyncio_run):
        mock_asyncio_run.return_value = [
            {'url': 'wss://relay.damus.io', 'success': True, 'response': 'OK'}
        ]

        event_id = self.publisher.publish_event("Test content")
        
        # Check if a job was created
        job = self.env['queue.job'].search([('name', '=', 'Publish Nostr Event')], limit=1)
        self.assertTrue(job)

        # Manually run the job
        self.publisher.publish_event_job(json.loads(job.args)[0], json.loads(job.args)[1])

        # Check if a log was created
        log = self.env['nostr.publish.log'].search([('event_id', '=', event_id)], limit=1)
        self.assertTrue(log)
        self.assertEqual(log.success_count, 1)
        self.assertEqual(log.total_relays, 1)

        # Check if the publisher stats were updated
        self.assertEqual(self.publisher.total_events_published, 1)
        self.assertEqual(self.publisher.success_count, 1)
        self.assertEqual(self.publisher.success_rate, 100)

    def test_compute_id(self):
        event = {
            'content': "Test content",
            'public_key': self.publisher.public_key,
            'created_at': 1234567890,
            'kind': 1,
            'tags': []
        }
        event_id = self.publisher.compute_id(event)
        self.assertTrue(isinstance(event_id, str))
        self.assertEqual(len(event_id), 64)  # SHA256 hash is 64 characters long

    def test_sign_event(self):
        event = {
            'id': 'a' * 64,  # mock event id
            'public_key': self.publisher.public_key,
        }
        signature = self.publisher.sign_event(event)
        self.assertTrue(isinstance(signature, str))
        self.assertEqual(len(signature), 128)  # Schnorr signature is 64 bytes (128 hex characters)

    def test_publish_event_inactive(self):
        self.publisher.state = 'inactive'
        with self.assertRaises(UserError):
            self.publisher.publish_event("Test content")

    def test_publish_event_no_relays(self):
        self.env['nostr.relay'].search([]).unlink()
        with self.assertRaises(UserError):
            self.publisher.publish_event("Test content")

    def test_compute_relay_count(self):
        self.assertEqual(self.publisher.relay_count, 1)
        self.env['nostr.relay'].create({
            'publisher_id': self.publisher.id,
            'url': 'wss://relay.nostrich.cc'
        })
        self.publisher._compute_relay_count()
        self.assertEqual(self.publisher.relay_count, 2)

    def test_compute_success_rate(self):
        self.publisher.total_events_published = 100
        self.publisher.success_count = 75
        self.publisher._compute_success_rate()
        self.assertEqual(self.publisher.success_rate, 75.0)

        self.publisher.total_events_published = 0
        self.publisher._compute_success_rate()
        self.assertEqual(self.publisher.success_rate, 0)

    @patch('odoo.addons.queue_job.job.Job.enqueue')
    def test_publish_event_for_module(self, mock_enqueue):
        mock_enqueue.return_value = MagicMock(uuid='test-job-uuid')
        
        event_id = self.NostrPublisher.publish_event_for_module('test_module', 'test_event', {'key': 'value'})
        
        self.assertTrue(event_id)
        mock_enqueue.assert_called_once()
        
        # Verify that the job was created with the correct method and arguments
        job_method = mock_enqueue.call_args[0][0]
        self.assertEqual(job_method.__name__, 'publish_event_job')
        
        job_args = mock_enqueue.call_args[0][1]
        self.assertIn('test_module', json.dumps(job_args))
        self.assertIn('test_event', json.dumps(job_args))

    @patch('odoo.addons.nostr_publisher.models.nostr_publisher.websockets.connect')
    def test_listen_for_events(self, mock_websocket):
        mock_recv = MagicMock(return_value=json.dumps(["EVENT", {}, {
            "id": "test_id",
            "content": json.dumps({
                "module": "test_module",
                "type": "test_event",
                "content": {"key": "value"}
            })
        }]))
        mock_websocket.return_value.__aenter__.return_value.recv = mock_recv
        
        with patch.object(self.NostrPublisher, 'dispatch_event') as mock_dispatch:
            self.NostrPublisher.listen_for_events()
            mock_dispatch.assert_called_once()

    def test_dispatch_event(self):
        event = {
            "id": "test_id",
            "content": json.dumps({
                "module": "test_module",
                "type": "test_event",
                "content": {"key": "value"}
            })
        }
        
        # Create a mock handler
        mock_handler = MagicMock()
        self.env['test_module.nostr_handler'] = mock_handler
        mock_handler.handle_nostr_event_test_event = MagicMock()
        
        self.NostrPublisher.dispatch_event(event)
        
        mock_handler.handle_nostr_event_test_event.assert_called_once_with({"key": "value"})

    @patch('odoo.addons.queue_job.job.Job.enqueue')
    def test_start_listening(self, mock_enqueue):
        mock_enqueue.return_value = MagicMock(uuid='test-job-uuid')
        
        self.NostrPublisher.start_listening()
        
        mock_enqueue.assert_called_once()
        
        # Verify that the job was created with the correct method
        job_method = mock_enqueue.call_args[0][0]
        self.assertEqual(job_method.__name__, 'listen_for_events')
