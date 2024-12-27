# tests/test_create_commit_wizard.py

import unittest
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import gitlab
from unittest.mock import patch, MagicMock

class TestCreateCommitWizard(TransactionCase):

    def setUp(self):
        super(TestCreateCommitWizard, self).setUp()
        self.repo = self.env['gitlab.repository'].create({
            'name': 'Test Repo',
            'gitlab_id': 1,
            'url': 'https://gitlab.com/test/repo',
            'project_id': 1
        })
        self.wizard = self.env['gitlab_nostr_bridge.create.commit.wizard'].create({
            'repository_id': self.repo.id,
            'branch_name': 'main',
            'commit_message': 'Test commit',
            'file_path': 'test.txt',
            'file_content': 'Test content'
        })

    @patch('odoo.addons.gitlab_nostr_bridge.wizards.create_commit_wizard.gitlab.Gitlab')
    def test_create_new_file(self, mock_gitlab):
        mock_project = MagicMock()
        mock_project.files.get.side_effect = gitlab.exceptions.GitlabGetError(response_code=404)
        mock_gitlab.return_value.projects.get.return_value = mock_project

        self.wizard._compute_file_exists()
        self.assertFalse(self.wizard.file_exists)

        mock_project.commits.create.return_value = MagicMock(id='new_commit_id')
        result = self.wizard.action_create_commit()

        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['params']['type'], 'success')
        mock_project.commits.create.assert_called_once()

    @patch('odoo.addons.gitlab_nostr_bridge.wizards.create_commit_wizard.gitlab.Gitlab')
    def test_update_existing_file(self, mock_gitlab):
        mock_project = MagicMock()
        mock_project.files.get.return_value = MagicMock()
        mock_gitlab.return_value.projects.get.return_value = mock_project

        self.wizard._compute_file_exists()
        self.assertTrue(self.wizard.file_exists)

        mock_project.commits.create.return_value = MagicMock(id='updated_commit_id')
        result = self.wizard.action_create_commit()

        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['params']['type'], 'success')
        mock_project.commits.create.assert_called_once()

    @patch('odoo.addons.gitlab_nostr_bridge.wizards.create_commit_wizard.gitlab.Gitlab')
    def test_create_file_already_exists(self, mock_gitlab):
        mock_project = MagicMock()
        mock_project.files.get.return_value = MagicMock()
        mock_gitlab.return_value.projects.get.return_value = mock_project

        self.wizard._compute_file_exists()
        self.assertTrue(self.wizard.file_exists)

        mock_project.commits.create.side_effect = gitlab.exceptions.GitlabCreateError()
        with self.assertRaises(UserError):
            self.wizard.action_create_commit()

    def test_create_commit_non_existent_branch(self):
        self.wizard.branch_name = 'non_existent_branch'
        with self.assertRaises(UserError):
            self.wizard.action_create_commit()

    def test_create_commit_invalid_file_path(self):
        self.wizard.file_path = '../invalid/path.txt'
        with self.assertRaises(UserError):
            self.wizard.action_create_commit()

    def test_create_commit_empty_content(self):
        self.wizard.file_content = ''
        result = self.wizard.action_create_commit()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['params']['type'], 'success')

    @patch('odoo.addons.gitlab_nostr_bridge.wizards.create_commit_wizard.gitlab.Gitlab')
    def test_create_commit_no_branches(self, mock_gitlab):
        mock_project = MagicMock()
        mock_project.branches.list.return_value = []
        mock_gitlab.return_value.projects.get.return_value = mock_project

        with self.assertRaises(UserError):
            self.wizard.action_create_commit()

if __name__ == '__main__':
    unittest.main()
