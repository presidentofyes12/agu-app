# integrated_ivcs/models/nostr_events.py

import json
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class NostrEvent(models.AbstractModel):
    _name = 'nostr.event'
    _description = 'Base Nostr Event'

    id = fields.Char(string='Event ID', required=True, readonly=True)
    pubkey = fields.Char(string='Public Key', required=True)
    created_at = fields.Integer(string='Created At', required=True)
    kind = fields.Integer(string='Kind', required=True)
    tags = fields.Text(string='Tags')
    content = fields.Text(string='Content')
    sig = fields.Char(string='Signature', required=True)

    @api.model
    def create(self, vals):
        if 'created_at' not in vals:
            vals['created_at'] = int(datetime.now().timestamp())
        return super(NostrEvent, self).create(vals)

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": json.loads(self.tags) if self.tags else [],
            "content": self.content,
            "sig": self.sig
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"]
        })

    @api.constrains('kind')
    def _check_kind(self):
        for record in self:
            if record.kind not in [31228, 31227, 3121, 3122, 3123]:
                raise ValidationError("Invalid event kind")

class NostrRepositoryAnchor(models.Model):
    _name = 'nostr.event.repository.anchor'
    _description = 'Nostr Repository Anchor Event'
    _inherit = 'nostr.event'

    kind = fields.Integer(default=31228, readonly=True)
    repo_name = fields.Char(string='Repository Name', required=True)
    description = fields.Text(string='Description')
    maintainers = fields.Many2many('res.users', string='Maintainers')

    @api.constrains('content')
    def _check_content(self):
        for record in self:
            try:
                content = json.loads(record.content)
                if 'action' not in content or content['action'] != 'create_repository':
                    raise ValidationError("Invalid content for Repository Anchor event")
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in content field")

    def to_json(self):
        json_data = super(NostrRepositoryAnchor, self).to_json()
        data = json.loads(json_data)
        data['content'] = json.dumps({
            "action": "create_repository",
            "repo_name": self.repo_name,
            "description": self.description,
            "maintainers": self.maintainers.mapped('nostr_public_key')
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        content = json.loads(data['content'])
        maintainer_ids = cls.env['res.users'].search([('nostr_public_key', 'in', content['maintainers'])]).ids
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"],
            "repo_name": content["repo_name"],
            "description": content["description"],
            "maintainers": [(6, 0, maintainer_ids)]
        })

class NostrBranchEvent(models.Model):
    _name = 'nostr.event.branch'
    _description = 'Nostr Branch Event'
    _inherit = 'nostr.event'

    kind = fields.Integer(default=31227, readonly=True)
    branch_name = fields.Char(string='Branch Name', required=True)
    action = fields.Selection([('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')], string='Action', required=True)

    @api.constrains('content')
    def _check_content(self):
        for record in self:
            try:
                content = json.loads(record.content)
                if 'action' not in content or content['action'] not in ['create_branch', 'update_branch', 'delete_branch']:
                    raise ValidationError("Invalid content for Branch event")
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in content field")

    def to_json(self):
        json_data = super(NostrBranchEvent, self).to_json()
        data = json.loads(json_data)
        data['content'] = json.dumps({
            "action": f"{self.action}_branch",
            "branch_name": self.branch_name
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        content = json.loads(data['content'])
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"],
            "branch_name": content["branch_name"],
            "action": content["action"].replace("_branch", "")
        })

class NostrCommitEvent(models.Model):
    _name = 'nostr.event.commit'
    _description = 'Nostr Commit Event'
    _inherit = 'nostr.event'

    kind = fields.Integer(default=3121, readonly=True)
    commit_hash = fields.Char(string='Commit Hash', required=True)
    message = fields.Text(string='Commit Message', required=True)
    author = fields.Char(string='Author', required=True)
    timestamp = fields.Datetime(string='Timestamp', required=True)

    @api.constrains('content')
    def _check_content(self):
        for record in self:
            try:
                content = json.loads(record.content)
                required_fields = ['hash', 'message', 'author', 'date']
                if not all(field in content for field in required_fields):
                    raise ValidationError("Missing required fields in Commit event content")
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in content field")

    def to_json(self):
        json_data = super(NostrCommitEvent, self).to_json()
        data = json.loads(json_data)
        data['content'] = json.dumps({
            "hash": self.commit_hash,
            "message": self.message,
            "author": self.author,
            "date": self.timestamp.isoformat()
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        content = json.loads(data['content'])
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"],
            "commit_hash": content["hash"],
            "message": content["message"],
            "author": content["author"],
            "timestamp": datetime.fromisoformat(content["date"])
        })

class NostrTreeEvent(models.Model):
    _name = 'nostr.event.tree'
    _description = 'Nostr Tree Event'
    _inherit = 'nostr.event'

    kind = fields.Integer(default=3122, readonly=True)
    tree_hash = fields.Char(string='Tree Hash', required=True)
    items = fields.Text(string='Tree Items', required=True)

    @api.constrains('content')
    def _check_content(self):
        for record in self:
            try:
                content = json.loads(record.content)
                if 'hash' not in content or 'items' not in content:
                    raise ValidationError("Missing required fields in Tree event content")
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in content field")

    def to_json(self):
        json_data = super(NostrTreeEvent, self).to_json()
        data = json.loads(json_data)
        data['content'] = json.dumps({
            "hash": self.tree_hash,
            "items": json.loads(self.items)
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        content = json.loads(data['content'])
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"],
            "tree_hash": content["hash"],
            "items": json.dumps(content["items"])
        })

class NostrBlobEvent(models.Model):
    _name = 'nostr.event.blob'
    _description = 'Nostr Blob Event'
    _inherit = 'nostr.event'

    kind = fields.Integer(default=3123, readonly=True)
    blob_hash = fields.Char(string='Blob Hash', required=True)
    size = fields.Integer(string='Blob Size', required=True)
    data = fields.Text(string='Blob Data', required=True)

    @api.constrains('content')
    def _check_content(self):
        for record in self:
            try:
                content = json.loads(record.content)
                if 'hash' not in content or 'size' not in content or 'data' not in content:
                    raise ValidationError("Missing required fields in Blob event content")
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in content field")

    def to_json(self):
        json_data = super(NostrBlobEvent, self).to_json()
        data = json.loads(json_data)
        data['content'] = json.dumps({
            "hash": self.blob_hash,
            "size": self.size,
            "data": self.data
        })
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        content = json.loads(data['content'])
        return cls.create({
            "id": data["id"],
            "pubkey": data["pubkey"],
            "created_at": data["created_at"],
            "kind": data["kind"],
            "tags": json.dumps(data["tags"]),
            "content": data["content"],
            "sig": data["sig"],
            "blob_hash": content["hash"],
            "size": content["size"],
            "data": content["data"]
        })
