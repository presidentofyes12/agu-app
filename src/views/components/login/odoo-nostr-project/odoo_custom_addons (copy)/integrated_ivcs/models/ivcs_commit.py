from odoo import models, fields, api
import json
from nostr.event import Event
from nostr.key import PrivateKey
import logging

_logger = logging.getLogger(__name__)

class IVCSCommit(models.Model):
    _name = 'ivcs.commit'
    _description = 'IVCS Commit'

    hash = fields.Char(string='Commit Hash', required=True)
    message = fields.Text(string='Commit Message', required=True)
    author = fields.Char(string='Author', required=True, default=lambda self: self.env.user.name)
    date = fields.Datetime(string='Commit Date', required=True, default=fields.Datetime.now)
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True, ondelete='cascade')
    version_id = fields.Many2one('ivcs.version', string='Associated Version')

    @api.model
    def create(self, vals):
        commit = super(IVCSCommit, self).create(vals)
        try:
            commit._create_nostr_commit_event()
        except Exception as e:
            _logger.error(f"Failed to create Nostr commit event: {str(e)}")
        return commit

    def _create_nostr_commit_event(self):
        if not self.item_id.nostr_private_key:
            _logger.warning(f"No Nostr private key set for IVCS Item {self.item_id.name}")
            return

        try:
            private_key = PrivateKey.from_nsec(self.item_id.nostr_private_key)
        except Exception as e:
            _logger.error(f"Invalid Nostr private key for IVCS Item {self.item_id.name}: {str(e)}")
            return

        event = Event(
            kind=3121,
            content=json.dumps({
                "hash": self.hash,
                "message": self.message,
                "author": self.author,
                "date": self.date.isoformat(),
            }),
            tags=[['r', self.item_id.repo_path]],
            public_key=private_key.public_key.hex()
        )
        private_key.sign_event(event)
        
        try:
            self.env['nostr.event'].create_and_publish(event)
            _logger.info(f"Nostr commit event created and published for commit {self.hash}")
        except Exception as e:
            _logger.error(f"Failed to create and publish Nostr event for commit {self.hash}: {str(e)}")
