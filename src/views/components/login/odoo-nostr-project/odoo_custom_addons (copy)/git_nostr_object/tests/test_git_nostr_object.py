from odoo.tests.common import TransactionCase
from datetime import datetime
import random
import string
import logging
import os

_logger = logging.getLogger(__name__)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_sha():
    """Generate a random 40-character SHA hash"""
    return ''.join(random.choices('0123456789abcdef', k=40))

def get_current_timestamp():
    """Return the current timestamp"""
    return int(datetime.now().timestamp())

def get_author(env):
    """Return the logged-in user's name as the author"""
    return env.user.name

def get_local_path():
    """Return the Odoo installation path as the local path"""
    return '/opt/odoo'

def generate_nostr_keys():
    """Generate random 64-character Nostr public and private keys for the logged-in user"""
    public_key = random_string(64)
    private_key = random_string(64)
    return public_key, private_key

def get_event_type(content):
    """Extract the event type from the first line of the content"""
    return int(content.split('\n')[0].strip('# '))

def get_event_name(content):
    """Extract the event name from the first line of the content"""
    return content.split('\n', 1)[0]

def check_method_existence(env, methods):
    """Check if the required methods exist in the corresponding models"""
    for model, method_name in methods.items():
        model_obj = env[model]
        if not hasattr(model_obj, method_name):
            return False, f"Method '{method_name}' not found in model '{model}'"
    return True, "All required methods found"

class TestGitNostrObject(TransactionCase):

    def setUp(self):
        super(TestGitNostrObject, self).setUp()
        self.GitRepository = self.env['git.repository']
        self.GitCommit = self.env['git.commit']
        self.GitTree = self.env['git.tree']
        self.GitBlob = self.env['git.blob']
        self.GitNostrEventObject = self.env['git_nostr.event.object']
        self.NostrKey = self.env['nostr.key']
        self.NostrRelay = self.env['nostr.relay']
        self.NostrProfile = self.env['nostr.profile']

        # Check if required methods exist in the corresponding models
        required_methods = {
            'git.repository': 'traverse_and_publish',
            'nostr.event.object': 'action_publish',
            'nostr.key': 'generate_key_pair',
            'nostr.key': 'sign_event'
        }
        success, message = check_method_existence(self.env, required_methods)
        if not success:
            self.fail(message)

    def test_git_nostr_object(self):
        _logger.info("Testing Git-Nostr Object module...")

        # Test Git Repository
        repo_name = f'Test Repo {random_string()}'
        repo_path = f'{get_local_path()}/custom_addons/git_nostr_object/tests/test_repo_{random_string()}'
        repo = self.GitRepository.create({
            'name': repo_name,
            'path': repo_path
        })
        _logger.info(f"Created Git Repository with ID: {repo.id}")

        # Test traverse_and_publish
        try:
            repo.traverse_and_publish()
            _logger.info("traverse_and_publish executed successfully")
        except Exception as e:
            _logger.error(f"Error in traverse_and_publish: {e}")

        # Test Git Commit
        commit_sha = generate_sha()
        commit_author = get_author(self.env)
        commit_timestamp = get_current_timestamp()
        commit_data = 'Test commit data'
        commit = self.GitCommit.create({
            'sha': commit_sha,
            'message': 'Test commit message',
            'author': commit_author,
            'timestamp': commit_timestamp,
            'data': commit_data
        })
        _logger.info(f"Created Git Commit with ID: {commit.id}")

        # Test Git Tree
        tree_sha = generate_sha()
        tree_data = 'Test tree data'
        tree = self.GitTree.create({
            'sha': tree_sha,
            'data': tree_data
        })
        _logger.info(f"Created Git Tree with ID: {tree.id}")

        # Test Git Blob
        blob_sha = generate_sha()
        blob_data = 'Test blob data'
        blob = self.GitBlob.create({
            'sha': blob_sha,
            'data': blob_data
        })
        _logger.info(f"Created Git Blob with ID: {blob.id}")

        # Test Nostr Event Object
        event_content = '# 1\nTest Nostr event content'
        event_type = get_event_type(event_content)
        event_tags = '[]'
        event_created_at = get_current_timestamp()
        event_signature = random_string(64)
        event_name = get_event_name(event_content)
        event = self.GitNostrEventObject.create({
            'kind': event_type,
            'content': event_content,
            'tags': event_tags,
            'created_at': event_created_at,
            'signature': event_signature,
            'name': event_name
        })
        _logger.info(f"Created Nostr Event Object with ID: {event.id}")

        # Test action_publish
        try:
            event.action_publish()
            _logger.info("action_publish executed successfully")
        except Exception as e:
            _logger.error(f"Error in action_publish: {e}")

    def test_nostr_auth(self):
        _logger.info("Testing Nostr Authentication module...")

        # Test Nostr Key
        public_key, private_key = generate_nostr_keys()
        key = self.NostrKey.create({
            'public_key': public_key,
            'private_key': private_key,
            'user_id': self.env.user.id
        })
        _logger.info(f"Created Nostr Key with ID: {key.id}")

        # Test Nostr Relay
        relay_url = f'wss://relay{random_string()}.com'
        relay = self.NostrRelay.create({
            'url': relay_url,
            'is_active': True
        })
        _logger.info(f"Created Nostr Relay with ID: {relay.id}")

        # Test Nostr Profile
        profile_name = f'Test Profile {random_string()}'
        profile_about = 'Test profile description'
        profile_picture = 'http://example.com/pic.jpg'
        profile = self.NostrProfile.create({
            'name': profile_name,
            'about': profile_about,
            'picture': profile_picture,
            'user_id': self.env.user.id
        })
        _logger.info(f"Created Nostr Profile with ID: {profile.id}")

        # Test generate_key_pair method
        try:
            result = self.NostrKey.generate_key_pair()
            _logger.info(f"Generated key pair: {result}")
        except Exception as e:
            _logger.error(f"Error in generate_key_pair: {e}")

        # Test sign_event method (assuming it exists)
        try:
            event_data = {
                'kind': 1,
                'content': 'Test content',
                'created_at': get_current_timestamp(),
                'tags': []
            }
            result = key.sign_event(event_data)
            _logger.info(f"Signed event: {result}")
        except Exception as e:
            _logger.error(f"Error in sign_event: {e}")

def test_git_nostr_object():
    test_case = TestGitNostrObject.create({})
    test_case.test_git_nostr_object()

def test_nostr_auth():
    test_case = TestGitNostrObject.create({})
    test_case.test_nostr_auth()

# This allows running the test from the Odoo shell
if __name__ == '__main__':
    test_git_nostr_object()
    test_nostr_auth()
