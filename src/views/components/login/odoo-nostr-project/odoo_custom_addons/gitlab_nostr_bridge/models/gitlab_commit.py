# models/gitlab_commit.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil import parser
from datetime import datetime, timezone
from nostr.event import Event
from nostr.key import PrivateKey
import time
import asyncio
import json
import logging
import hashlib

_logger = logging.getLogger(__name__)

class GitlabCommit(models.Model):
    _name = 'gitlab.commit'
    _description = 'GitLab Commit'

    name = fields.Char(string='Commit Hash', required=True, readonly=True)
    message = fields.Text(string='Commit Message', required=True)
    author = fields.Char(string='Author', required=True)
    admin_id = fields.Many2one('res.users', string='Admin (Odoo User)')
    date = fields.Datetime(string='Commit Date', required=True)
    repository_id = fields.Many2one('gitlab.repository', string='Repository', required=True)
    branch_ids = fields.Many2many('gitlab.branch', string='Branches')
    repository_short = fields.Char(compute='_compute_repository_short', string='Repo')

    @api.depends('repository_id.name')
    def _compute_repository_short(self):
        for record in self:
            if record.repository_id.name:
                record.repository_short = record.repository_id.name[:10] + '...' if len(record.repository_id.name) > 10 else record.repository_id.name
            else:
                record.repository_short = ''

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._generate_commit_hash(vals)
        if not vals.get('author'):
            vals['author'] = self.env.user.name
        if not vals.get('admin_id'):
            vals['admin_id'] = self.env.user.id
        if not vals.get('date'):
            vals['date'] = fields.Datetime.now()
        return super(GitlabCommit, self).create(vals)

    def _generate_commit_hash(self, vals):
        hash_input = f"{vals.get('message', '')}{vals.get('author', '')}{fields.Datetime.now()}"
        return hashlib.sha1(hash_input.encode()).hexdigest()

    @api.model
    def create_or_update_from_gitlab(self, repository_id, gitlab_commit):
        _logger.info(f"Processing GitLab commit: {gitlab_commit.id} for repository {repository_id}")
        try:
            existing_commit = self.search([('name', '=', gitlab_commit.id), ('repository_id', '=', repository_id)])
            commit_date = self._convert_to_naive_datetime(gitlab_commit.committed_date)
            
            admin_user = self.env['res.users'].search([('email', '=', gitlab_commit.author_email)], limit=1)
            if not admin_user:
                _logger.warning(f"No matching Odoo user found for GitLab commit author: {gitlab_commit.author_name} ({gitlab_commit.author_email})")
            
            commit_data = {
                'name': gitlab_commit.id,
                'message': gitlab_commit.message,
                'author': gitlab_commit.author_name,
                'admin_id': admin_user.id if admin_user else False,
                'date': commit_date,
                'repository_id': repository_id,
            }
            
            if existing_commit:
                _logger.info(f"Updating existing commit: {gitlab_commit.id}")
                existing_commit.write(commit_data)
                commit = existing_commit
            else:
                _logger.info(f"Creating new commit: {gitlab_commit.id}")
                commit = self.create(commit_data)
            
            self._create_and_publish_nostr_event(commit)
            return commit
        
        except Exception as e:
            _logger.error(f"Error processing GitLab commit {gitlab_commit.id} for repository {repository_id}", exc_info=True)
            raise UserError(_("Failed to process GitLab commit: %s") % str(e))

    def _create_and_publish_nostr_event(self, commit):
        user = self.env.user
        if not user.nostr_private_key:
            _logger.error(f"Nostr private key is not set for the user {user.name} (ID: {user.id})")
            return

        try:
            private_key = PrivateKey.from_nsec(user.nostr_private_key)
            pub_key = private_key.public_key.hex()

            event = Event(
                public_key=pub_key,
                created_at=int(time.time()),
                kind=1,
                tags=[['r', commit.repository_id.url], ['c', commit.name]],
                content=f"New commit in repository {commit.repository_id.name}: {commit.message}. Hash: {commit.name}. Time of commit: " + str(int(time.time())) + "."
            )
            private_key.sign_event(event)

            relay_urls = self.env['ir.config_parameter'].sudo().get_param('nostr_bridge.relay_urls', '').split(',')
            relay_urls = [url.strip() for url in relay_urls if url.strip()]

            if not relay_urls:
                _logger.error("No Nostr relay URLs configured.")
                return

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self._publish_to_relays(relay_urls, event))

            successes = [result for result in results if result['success']]
            if successes:
                _logger.info(f"Successfully published Nostr event for commit {commit.name} to {len(successes)} out of {len(relay_urls)} relays.")
            else:
                _logger.error(f"Failed to publish Nostr event for commit {commit.name} to any relay.")

            for result in results:
                if not result['success']:
                    _logger.warning(f"Failed to publish to relay {result['url']}: {result.get('error', 'Unknown error')}")

        except Exception as e:
            _logger.error(f"Error creating and publishing Nostr event for commit {commit.name}: {str(e)}", exc_info=True)

    async def _publish_to_relays(self, relay_urls, event):
        import websockets

        async def publish_to_relay(url, event):
            try:
                async with websockets.connect(url.strip(), ping_interval=None) as websocket:
                    message = event.to_message()
                    await websocket.send(message)
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    return {'success': True, 'url': url, 'response': response}
            except Exception as e:
                return {'success': False, 'url': url, 'error': str(e)}

        tasks = [publish_to_relay(url, event) for url in relay_urls]
        return await asyncio.gather(*tasks)

    def _convert_to_naive_datetime(self, date_string):
        dt = parser.parse(date_string)
        return dt.replace(tzinfo=None)

    def publish_to_nostr(self):
        self.ensure_one()
        try:
            nostr_content = json.dumps({
                "commit_hash": self.name,
                "repository_path": self.repository_id.url,
                "commit_timestamp": int(self.date.timestamp())
            })

            self.env['nostr.publisher'].publish_event_for_module(
                module_name='gitlab_nostr_bridge',
                event_type='commit',
                content=nostr_content,
                tags=[['r', self.repository_id.url]]
            )
            _logger.info(f"Nostr event published for commit: {self.name}")
        except Exception as e:
            _logger.error(f"Failed to publish Nostr event for commit {self.name}: {str(e)}", exc_info=True)
            raise UserError(_("Failed to publish commit to Nostr: %s") % str(e))

    @api.constrains('name', 'repository_id')
    def _check_unique_commit(self):
        for record in self:
            if self.search_count([('name', '=', record.name), ('repository_id', '=', record.repository_id.id)]) > 1:
                raise ValidationError(_("A commit with this hash already exists for the selected repository."))

    @api.model
    def create_from_wizard(self, wizard_data):
        commit_data = {
            'message': wizard_data.get('commit_message'),
            'repository_id': wizard_data.get('repository_id'),
            'date': wizard_data.get('commit_date') or fields.Datetime.now(),
            'branch_ids': [(6, 0, wizard_data.get('branch_ids', []))],
        }
        return self.create(commit_data)
