from odoo import models, fields, api
import os
import shutil
import datetime

class AtomBackup(models.Model):
    _name = 'atom.backup'
    _description = 'Atom Backup'

    name = fields.Char(string='Backup Name', required=True)
    date = fields.Datetime(string='Backup Date', default=fields.Datetime.now)
    file_path = fields.Char(string='Backup File Path')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('restored', 'Restored')
    ], string='State', default='draft')

    @api.model
    def schedule_backup(self):
        backup_dir = self.env['ir.config_parameter'].sudo().get_param('atom.backup_dir', '/opt/atom_backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        db_name = self.env.cr.dbname
        file_name = f"{db_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        file_path = os.path.join(backup_dir, file_name)

        self._cr.execute("SELECT * FROM atom_atom")
        with open(file_path, 'w') as f:
            shutil.copyfileobj(self._cr.copy_expert(f"COPY atom_atom TO STDOUT WITH CSV HEADER"), f)

        self.create({
            'name': file_name,
            'file_path': file_path,
            'state': 'done'
        })

    def restore_backup(self):
        self.ensure_one()
        if self.state != 'done':
            raise UserError("Can only restore 'Done' backups.")

        self._cr.execute("TRUNCATE atom_atom")
        with open(self.file_path, 'r') as f:
            self._cr.copy_expert("COPY atom_atom FROM STDIN WITH CSV HEADER", f)

        self.state = 'restored'