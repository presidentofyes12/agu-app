from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestRepositoryAnchor(TransactionCase):

    def setUp(self):
        super(TestRepositoryAnchor, self).setUp()
        self.repo_manager = self.env['git.repository.manager'].sudo()
        self.user_admin = self.env.ref('base.user_admin')
        self.user_demo = self.env.ref('base.user_demo')

    def test_create_repository(self):
        repo_id = self.repo_manager.create_repository(
            "test-repo", "/path/to/test-repo", "Test repository", [self.user_admin.id]
        )
        repo = self.env['git.repository'].browse(repo_id)
        self.assertEqual(repo.name, "test-repo")
        self.assertEqual(repo.path, "/path/to/test-repo")
        self.assertEqual(repo.description, "Test repository")
        self.assertIn(self.user_admin, repo.maintainer_ids)
        self.assertEqual(len(repo.branch_ids), 1)
        self.assertEqual(repo.branch_ids[0].name, 'main')

    def test_update_repository(self):
        repo_id = self.repo_manager.create_repository(
            "test-repo", "Test repository", [self.user_admin.id]
        )
        updated_repo_id = self.repo_manager.update_repository(
            repo_id, "Updated description", [self.user_admin.id, self.user_demo.id]
        )
        repo = self.env['git.repository'].browse(updated_repo_id)
        self.assertEqual(repo.description, "Updated description")
        self.assertIn(self.user_demo, repo.maintainer_ids)

    def test_fork_repository(self):
        original_repo_id = self.repo_manager.create_repository(
            "original-repo", "Original repository", [self.user_admin.id]
        )
        forked_repo_id = self.repo_manager.fork_repository(
            original_repo_id, "forked-repo", self.user_demo.id
        )
        forked_repo = self.env['git.repository'].browse(forked_repo_id)
        self.assertEqual(forked_repo.name, "forked-repo")
        self.assertIn(self.user_demo, forked_repo.maintainer_ids)
        self.assertEqual(len(forked_repo.branch_ids), 1)
        self.assertEqual(forked_repo.branch_ids[0].name, 'main')

    def test_list_maintainers(self):
        repo_id = self.repo_manager.create_repository(
            "test-repo", "Test repository", [self.user_admin.id, self.user_demo.id]
        )
        maintainer_ids = self.repo_manager.list_maintainers(repo_id)
        self.assertIn(self.user_admin.id, maintainer_ids)
        self.assertIn(self.user_demo.id, maintainer_ids)

    def test_access_rights(self):
        repo_id = self.repo_manager.create_repository(
            "test-repo", "Test repository", [self.user_admin.id]
        )
        
        # Test that non-maintainer can't update the repository
        with self.assertRaises(AccessError):
            self.repo_manager.with_user(self.user_demo).update_repository(
                repo_id, "Unauthorized update"
            )

        # Test that maintainer can update the repository
        self.repo_manager.with_user(self.user_admin).update_repository(
            repo_id, "Authorized update"
        )
        repo = self.env['git.repository'].browse(repo_id)
        self.assertEqual(repo.description, "Authorized update")
