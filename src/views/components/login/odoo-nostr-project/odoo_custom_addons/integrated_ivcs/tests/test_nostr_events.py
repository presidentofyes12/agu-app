# integrated_ivcs/tests/test_nostr_events.py

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import json

class TestNostrEvents(TransactionCase):

    def setUp(self):
        super(TestNostrEvents, self).setUp()
        self.RepositoryAnchor = self.env['nostr.event.repository.anchor']
        self.BranchEvent = self.env['nostr.event.branch']
        self.CommitEvent = self.env['nostr.event.commit']
        self.TreeEvent = self.env['nostr.event.tree']
        self.BlobEvent = self.env['nostr.event.blob']

    def test_repository_anchor_event(self):
        event = self.RepositoryAnchor.create({
            'id': 'test_id',
            'pubkey': 'test_pubkey',
            'sig': 'test_sig',
            'repo_name': 'test_repo',
            'description': 'Test repository',
            'content': json.dumps({
                'action': 'create_repository',
                'repo_name': 'test_repo',
                'description': 'Test repository'
            })
        })
        self.assertEqual(event.kind, 31228)
        
        json_str = event.to_json()
        new_event = self.RepositoryAnchor.from_json(json_str)
        self.assertEqual(new_event.repo_name, 'test_repo')
        
        with self.assertRaises(ValidationError):
            self.RepositoryAnchor.create({
                'id': 'test_id',
                'pubkey': 'test_pubkey',
                'sig': 'test_sig',
                'repo_name': 'test_repo',
                'description': 'Test repository',
                'content': json.dumps({
                    'action': 'invalid_action',
                    'repo_name': 'test_repo',
                    'description': 'Test repository'
                })
            })

    def test_branch_event(self):
        event = self.BranchEvent.create({
            'id': 'test_id',
            'pubkey': 'test_pubkey',
            'sig': 'test_sig',
            'branch_name': 'test_branch',
            'action': 'create',
            'content': json.dumps({
                'action': 'create_branch',
                'branch_name': 'test_branch'
            })
        })
        self.assertEqual(event.kind, 31227)
        
        json_str = event.to_json()
        new_event = self.BranchEvent.from_json(json_str)
        self.assertEqual(new_event.branch_name, 'test_branch')
        self.assertEqual(new_event.action, 'create')
        
        with self.assertRaises(ValidationError):
            self.BranchEvent.create({
                'id': 'test_id',
                'pubkey': 'test_pubkey',
                'sig': 'test_sig',
                'branch_name': 'test_branch',
                'action': 'create',
                'content': json.dumps({
                    'action': 'invalid_action',
                    'branch_name': 'test_branch'
                })
            })

    def test_commit_event(self):
        event = self.CommitEvent.create({
            'id': 'test_id',
            'pubkey': 'test_pubkey',
            'sig': 'test_sig',
            'commit_hash': 'test_hash',
            'message': 'Test commit',
            'author': 'Test Author',
            'timestamp': '2023-06-01 12:00:00',
            'content': json.dumps({
                'hash': 'test_hash',
                'message': 'Test commit',
                'author': 'Test Author',
                'date': '2023-06-01T12:00:00'
            })
        })
        self.assertEqual(event.kind, 3121)
        
        json_str = event.to_json()
        new_event = self.CommitEvent.from_json(json_str)
        self.assertEqual(new_event.commit_hash, 'test_hash')
        self.assertEqual(new_event.message, 'Test commit')
        
        with self.assertRaises(ValidationError):
            self.CommitEvent.create({
                'id': 'test_id',
                'pubkey': 'test_pubkey',
                'sig': 'test_sig',
                'commit_hash': 'test_hash',
                'message': 'Test commit',
                'author': 'Test Author',
                'timestamp': '2023-06-01 12:00:00',
                'content': json.dumps({
                    'hash': 'test_hash',
                    'message': 'Test commit'
                    # Missing 'author' and 'date' fields
                })
            })

    def test_tree_event(self):
        event = self.TreeEvent.create({
            'id': 'test_id',
            'pubkey': 'test_pubkey',
            'sig': 'test_sig',
            'tree_hash': 'test_hash',
            'items': json.dumps([{'path': 'file1', 'mode': '100644', 'type': 'blob', 'sha': 'file1_hash'}]),
            'content': json.dumps({
                'hash': 'test_hash',
                'items': [{'path': 'file1', 'mode': '100644', 'type': 'blob', 'sha': 'file1_hash'}]
            })
        })
        self.assertEqual(event.kind, 3122)
        
        json_str = event.to_json()
        new_event = self.TreeEvent.from_json(json_str)
        self.assertEqual(new_event.tree_hash, 'test_hash')
        self.assertIn('file1', new_event.items)
        
        with self.assertRaises(ValidationError):
            self.TreeEvent.create({
                'id': 'test_id',
                'pubkey': 'test_pubkey',
                'sig': 'test_sig',
                'tree_hash': 'test_hash',
                'items': json.dumps([{'path': 'file1', 'mode': '100644', 'type': 'blob', 'sha': 'file1_hash'}]),
                'content': json.dumps({
                    'hash': 'test_hash'
                    # Missing 'items' field
                })
            })

    def test_blob_event(self):
        event = self.BlobEvent.create({
            'id': 'test_id',
            'pubkey': 'test_pubkey',
            'sig': 'test_sig',
            'blob_hash': 'test_hash',
            'size': 100,
            'data': 'Test blob data',
            'content': json.dumps({
                'hash': 'test_hash',
                'size': 100,
                'data': 'Test blob data'
            })
        })
        self.assertEqual(event.kind, 3123)
        
        json_str = event.to_json()
        new_event = self.BlobEvent.from_json(json_str)
        self.assertEqual(new_event.blob_hash, 'test_hash')
        self.assertEqual(new_event.size, 100)
        self.assertEqual(new_event.data, 'Test blob data')
        
        with self.assertRaises(ValidationError):
            self.BlobEvent.create({
                'id': 'test_id',
                'pubkey': 'test_pubkey',
                'sig': 'test_sig',
                'blob_hash': 'test_hash',
                'size': 100,
                'data': 'Test blob data',
                'content': json.dumps({
                    'hash': 'test_hash',
                    'size': 100
                    # Missing 'data' field
                })
            })
