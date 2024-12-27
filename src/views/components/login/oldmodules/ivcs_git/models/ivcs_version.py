# File: ivcs_version.py

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
import git
import os
import logging

_logger = logging.getLogger(__name__)

class IVCSVersion(models.Model):
    _name = 'ivcs.version'
    _description = 'IVCS Version'

    name = fields.Char('Version Name', required=True)
    description = fields.Text('Description')
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True, ondelete='cascade')
    parent_id = fields.Many2one('ivcs.version', string='Parent Version')
    child_ids = fields.One2many('ivcs.version', 'parent_id', string='Child Versions')
    commit_hash = fields.Char('Commit Hash', readonly=True)
    create_date = fields.Datetime('Created On', readonly=True, default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('released', 'Released'),
        ('deprecated', 'Deprecated')
    ], string='Status', default='draft', required=True)
    active = fields.Boolean(default=True)
    metadata_ids = fields.One2many('ivcs.metadata', 'version_id', string='Metadata')

    @api.constrains('item_id')
    def _check_item_id(self):
        for record in self:
            if not record.item_id:
                raise ValidationError(_("A version must be associated with an IVCS item."))

    def unlink(self):
        for record in self:
            if record == record.item_id.current_version_id:
                raise UserError(_("Cannot delete the current version of an IVCS item. Please set another version as current before deleting."))
        return self.write({'active': False})

    def archive_version(self):
        for record in self:
            if record == record.item_id.current_version_id:
                raise UserError(_("Cannot archive the current version of an IVCS item. Please set another version as current before archiving."))
            record.active = False

    def action_unarchive(self):
        return self.write({'active': True})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('item_id'):
                raise ValidationError(_("A version must be associated with an IVCS item."))
            if not vals.get('name'):
                vals['name'] = 'v1.0'
        
        versions = super(IVCSVersion, self).create(vals_list)
        return versions

    def _create_commit(self):
        self.ensure_one()
        if not self.item_id or not self.item_id.repo_path:
            _logger.warning(f"Cannot create commit for version {self.id}: missing item or repo path")
            return
        try:
            repo = git.Repo(self.item_id.repo_path)
            readme_path = os.path.join(self.item_id.repo_path, 'README.md')
            with open(readme_path, 'w') as f:
                f.write(f"# {self.item_id.name} - {self.name}\n\n{self.description}")
            repo.index.add(['README.md'])
            commit = repo.index.commit(f"Version {self.name}: {self.description}")
            self.commit_hash = commit.hexsha
            _logger.info(f"Created commit {commit.hexsha} for version {self.id}")
        except Exception as e:
            _logger.error(f"Failed to create commit for version {self.id}: {str(e)}")
            raise UserError(_("Failed to create commit: %s") % str(e))

    def release_version(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft versions can be released."))
        self.state = 'released'

    def deprecate_version(self):
        self.ensure_one()
        if self.state != 'released':
            raise UserError(_("Only released versions can be deprecated."))
        self.state = 'deprecated'
