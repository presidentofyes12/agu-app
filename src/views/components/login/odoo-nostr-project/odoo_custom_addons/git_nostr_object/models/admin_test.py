# /opt/odoo/custom_addons/git_nostr_object/models/admin_test.py
from odoo import models, api
from ..tests.test_git_nostr_object import test_git_nostr_object, test_nostr_auth

class AdminTest(models.TransientModel):
    _name = 'git_nostr_object.admin_test'
    _description = 'Admin Test for Git-Nostr Object'

    def run_tests(self):
        test_git_nostr_object()
        test_nostr_auth()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test Results',
                'message': 'Tests completed. Check the logs for details.',
                'sticky': False,
            }
        }
