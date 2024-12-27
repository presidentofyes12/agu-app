from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.event import Event
from nostr.key import PrivateKey
import json
import os
import logging
import time
from functools import wraps  # Add this import

_logger = logging.getLogger(__name__)

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        _logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

class RepositoryAnchor(models.AbstractModel):
    _name = 'git.repository.anchor'
    _description = 'Git Repository Anchor'

    @api.model
    def _get_private_key(self):
        # In practice, you'd retrieve this securely
        return PrivateKey()

    @log_execution_time
    def create_anchor_event(self, repo_path, maintainers):
        _logger.info(f"Creating anchor event for repository: {repo_path}")
        start_time = time.time()

        private_key = self._get_private_key()
        content = json.dumps({
            "action": "create_repository",
            "repo_name": os.path.basename(repo_path),
            "maintainers": maintainers
        })
        event = Event(
            kind=31228,
            content=content,
            tags=[['r', repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)

        end_time = time.time()
        _logger.info(f"Anchor event created in {end_time - start_time:.2f} seconds")
        return event

    def update_anchor(self, repo_path, maintainers):
        _logger.info(f"Updating anchor for repository: {repo_path}")
        start_time = time.time()

        private_key = self._get_private_key()
        content = json.dumps({
            "action": "update_repository",
            "repo_name": os.path.basename(repo_path),
            "maintainers": maintainers
        })
        event = Event(
            kind=31228,
            content=content,
            tags=[['r', repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)

        end_time = time.time()
        _logger.info(f"Anchor updated in {end_time - start_time:.2f} seconds")
        return event

    def resolve_repository_state(self, anchor_event):
        _logger.info("Resolving repository state from anchor event")
        start_time = time.time()

        try:
            content = json.loads(anchor_event.content)
            state = {
                "repo_name": content["repo_name"],
                "maintainers": content["maintainers"]
            }
        except json.JSONDecodeError as e:
            _logger.error(f"Error decoding anchor event content: {str(e)}")
            raise UserError(_("Invalid anchor event content"))
        except KeyError as e:
            _logger.error(f"Missing key in anchor event content: {str(e)}")
            raise UserError(_("Incomplete anchor event content"))

        end_time = time.time()
        _logger.info(f"Repository state resolved in {end_time - start_time:.2f} seconds")
        return state

    def list_maintainers(self, anchor_event):
        _logger.info("Listing maintainers from anchor event")
        start_time = time.time()

        try:
            content = json.loads(anchor_event.content)
            maintainers = content["maintainers"]
        except json.JSONDecodeError as e:
            _logger.error(f"Error decoding anchor event content: {str(e)}")
            raise UserError(_("Invalid anchor event content"))
        except KeyError:
            _logger.error("Maintainers key not found in anchor event content")
            raise UserError(_("Incomplete anchor event content"))

        end_time = time.time()
        _logger.info(f"Maintainers listed in {end_time - start_time:.2f} seconds")
        return maintainers

    def check_permission(self, anchor_event, public_key):
        _logger.info(f"Checking permission for public key: {public_key}")
        start_time = time.time()

        maintainers = self.list_maintainers(anchor_event)
        has_permission = public_key in maintainers

        end_time = time.time()
        _logger.info(f"Permission check completed in {end_time - start_time:.2f} seconds")
        return has_permission

    def fork_repository(self, original_repo_path, new_repo_path, new_maintainers):
        _logger.info(f"Forking repository from {original_repo_path} to {new_repo_path}")
        start_time = time.time()

        private_key = self._get_private_key()
        content = json.dumps({
            "action": "fork_repository",
            "original_repo": original_repo_path,
            "new_repo": new_repo_path,
            "maintainers": new_maintainers
        })
        event = Event(
            kind=31228,
            content=content,
            tags=[['r', new_repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)

        end_time = time.time()
        _logger.info(f"Repository forked in {end_time - start_time:.2f} seconds")
        return event
