import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .git_operations import GitOperations
from .nostr_event import NostrEvent
import json
import time
import traceback

logger = logging.getLogger(__name__)

class BranchManager(models.Model):
    _name = 'ivcs.branch.manager'
    _description = 'IVCS Branch Manager'

    name = fields.Char(string='Name', required=True)
    ivcs_item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    private_key = fields.Char(string='Nostr Private Key')
    public_key = fields.Char(string='Nostr Public Key', compute='_compute_public_key')

    @api.depends('private_key')
    def _compute_public_key(self):
        for record in self:
            if record.private_key:
                try:
                    public_key = NostrEvent.get_public_key(record.private_key)
                    record.public_key = public_key
                except Exception as e:
                    logger.error(f"Error computing public key: {str(e)}")
                    record.public_key = False
            else:
                record.public_key = False

    def create_branch(self, branch_name):
        self.ensure_one()
        start_time = time.time()
        logger.info(f"Starting to create branch: {branch_name}")

        try:
            git_ops = GitOperations(self.ivcs_item_id.repo_path)
            new_branch = git_ops.create_branch(branch_name)

            event = self._generate_nostr_event('create', branch_name)
            self._publish_nostr_event(event)

            self.ivcs_item_id.create_branch(branch_name)

            end_time = time.time()
            logger.info(f"Branch {branch_name} created successfully. Time taken: {end_time - start_time:.2f} seconds")

            return {'status': 'success', 'message': f"Branch {branch_name} created successfully"}
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to create branch: {str(e)}"))

    def update_branch(self, branch_name):
        self.ensure_one()
        start_time = time.time()
        logger.info(f"Starting to update branch: {branch_name}")

        try:
            git_ops = GitOperations(self.ivcs_item_id.repo_path)
            git_ops.update_branch(branch_name)

            event = self._generate_nostr_event('update', branch_name)
            self._publish_nostr_event(event)

            self.ivcs_item_id.sync_repository()

            end_time = time.time()
            logger.info(f"Branch {branch_name} updated successfully. Time taken: {end_time - start_time:.2f} seconds")

            return {'status': 'success', 'message': f"Branch {branch_name} updated successfully"}
        except Exception as e:
            logger.error(f"Error updating branch {branch_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to update branch: {str(e)}"))

    def list_branches(self):
        self.ensure_one()
        start_time = time.time()
        logger.info("Starting to list branches")

        try:
            git_ops = GitOperations(self.ivcs_item_id.repo_path)
            branches = git_ops.list_branches()

            end_time = time.time()
            logger.info(f"Branches listed successfully. Time taken: {end_time - start_time:.2f} seconds")

            return branches
        except Exception as e:
            logger.error(f"Error listing branches: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to list branches: {str(e)}"))

    def reconstruct_branches_from_events(self):
        self.ensure_one()
        start_time = time.time()
        logger.info("Starting to reconstruct branches from events")

        try:
            nostr_events = self.env['nostr.event'].search([('kind', '=', 31227)])
            events = [self._convert_to_nostr_event(event) for event in nostr_events]

            git_ops = GitOperations(self.ivcs_item_id.repo_path)

            for event in events:
                event_data = json.loads(event['content'])
                if event_data['action'] == 'create':
                    git_ops.create_branch(event_data['branch'])
                elif event_data['action'] == 'update':
                    git_ops.update_branch(event_data['branch'])

            self.ivcs_item_id.sync_repository()

            end_time = time.time()
            logger.info(f"Branches reconstructed successfully. Time taken: {end_time - start_time:.2f} seconds")

            return {'status': 'success', 'message': "Branches reconstructed successfully from events"}
        except Exception as e:
            logger.error(f"Error reconstructing branches from events: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to reconstruct branches: {str(e)}"))

    def _generate_nostr_event(self, action, branch_name):
        try:
            content = json.dumps({
                "action": action,
                "branch": branch_name,
                "repo": self.ivcs_item_id.repo_path
            })

            event = NostrEvent.create_event(
                kind=31227,
                content=content,
                tags=[["r", self.ivcs_item_id.repo_path]],
                private_key=self.private_key
            )

            logger.info(f"Generated Nostr event for {action} on branch {branch_name}")

            return event
        except Exception as e:
            logger.error(f"Error generating Nostr event: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to generate Nostr event: {str(e)}"))

    def _publish_nostr_event(self, event):
        try:
            nostr_adapter = self.env['nostr.adapter'].sudo()
            result = nostr_adapter.publish_event(event)

            if result:
                logger.info(f"Successfully published Nostr event: {event['id']}")
                return {'status': 'success', 'message': "Nostr event published successfully"}
            else:
                logger.warning(f"Failed to publish Nostr event: {event['id']}")
                return {'status': 'error', 'message': "Failed to publish Nostr event"}
        except Exception as e:
            logger.error(f"Error publishing Nostr event: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to publish Nostr event: {str(e)}"))

    def _convert_to_nostr_event(self, odoo_event):
        try:
            tags = json.loads(odoo_event.tags) if odoo_event.tags else []
            return {
                'id': odoo_event.event_id,
                'kind': odoo_event.kind,
                'content': odoo_event.content,
                'tags': tags,
                'public_key': odoo_event.public_key,
                'created_at': odoo_event.created_at,
                'signature': odoo_event.signature
            }
        except Exception as e:
            logger.error(f"Error converting Odoo event to Nostr event: {str(e)}")
            logger.error(traceback.format_exc())
            raise UserError(_(f"Failed to convert Odoo event to Nostr event: {str(e)}"))
