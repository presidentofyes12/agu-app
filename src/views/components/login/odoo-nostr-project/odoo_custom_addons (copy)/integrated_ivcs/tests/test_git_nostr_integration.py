import unittest
import tempfile
import os
import git
import json
from nostr.event import Event
from nostr.key import PrivateKey
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestGitNostrIntegration(TransactionCase):

    def setUp(self):
        super(TestGitNostrIntegration, self).setUp()
        self.IVCSItem = self.env['ivcs.item']
        self.NostrEvent = self.env['nostr.event']
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.temp_dir, 'test_repo')

    def tearDown(self):
        super(TestGitNostrIntegration, self).tearDown()
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def test_create_repository(self):
        item = self.IVCSItem.create({
            'name': 'Test Repo',
            'description': 'Test repository',
            'repo_path': self.repo_path,
        })
        self.assertTrue(os.path.exists(self.repo_path))
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, '.git')))
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, 'README.md')))

    def test_create_branch(self):
        item = self.IVCSItem.create({
            'name': 'Test Repo',
            'description': 'Test repository',
            'repo_path': self.repo_path,
        })
        result = item.create_branch('test-branch')
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['params']['type'], 'success')
        repo = git.Repo(self.repo_path)
        self.assertIn('test-branch', repo.heads)

    def test_merge_branches(self):
        item = self.IVCSItem.create({
            'name': 'Test Repo',
            'description': 'Test repository',
            'repo_path': self.repo_path,
        })
        item.create_branch('branch1')
        item.create_branch('branch2')
        repo = git.Repo(self.repo_path)
        repo.heads.branch1.checkout()
        with open(os.path.join(self.repo_path, 'file1.txt'), 'w') as f:
            f.write('Content in branch1')
        repo.index.add(['file1.txt'])
        repo.index.commit('Commit in branch1')
        
        result = item.merge_branches('branch1', 'branch2')
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['params']['type'], 'success')
        
        repo.heads.branch2.checkout()
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, 'file1.txt')))

    def test_create_nostr_events(self):
        item = self.IVCSItem.create({
            'name': 'Test Repo',
            'description': 'Test repository',
            'repo_path': self.repo_path,
        })
        repo = git.Repo(self.repo_path)
        with open(os.path.join(self.repo_path, 'test.txt'), 'w') as f:
            f.write('Test content')
        repo.index.add(['test.txt'])
        commit = repo.index.commit('Test commit')
        
        event = self.NostrEvent.create_git_event(self.repo_path, commit.hexsha)
        self.assertEqual(event.kind, 3121)
        self.assertIn(commit.hexsha, event.content)

    def test_reconstruct_git_objects(self):
        item = self.IVCSItem.create({
            'name': 'Test Repo',
            'description': 'Test repository',
            'repo_path': self.repo_path,
        })
        repo = git.Repo(self.repo_path)
        with open(os.path.join(self.repo_path, 'test.txt'), 'w') as f:
            f.write('Test content')
        repo.index.add(['test.txt'])
        commit = repo.index.commit('Test commit')
        
        self.NostrEvent.create_git_event(self.repo_path, commit.hexsha)
        
        # Delete the .git directory to simulate a fresh repository
        import shutil
        shutil.rmtree(os.path.join(self.repo_path, '.git'))
        
        # Reconstruct the repository from Nostr events
        self.NostrEvent.reconstruct_git_objects(self.repo_path)
        
        reconstructed_repo = git.Repo(self.repo_path)
        self.assertIn(commit.hexsha, reconstructed_repo.heads.master.commit.hexsha)
        self.assertTrue(os.path.exists(os.path.join(self.repo_path, 'test.txt')))

if __name__ == '__main__':
    unittest.main()
