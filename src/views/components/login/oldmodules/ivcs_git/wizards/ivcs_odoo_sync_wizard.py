from odoo import models, fields, api

class IVCSOdooSyncWizard(models.TransientModel):
    _name = 'ivcs.odoo.sync.wizard'
    _description = 'IVCS Odoo Sync Wizard'

    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True)
    odoo_instance_url = fields.Char(string="Odoo Instance URL", required=True)
    odoo_database = fields.Char(string="Odoo Database", required=True)
    odoo_login = fields.Char(string="Odoo Login", required=True)
    odoo_password = fields.Char(string="Odoo Password", required=True)

    def action_sync(self):
        self.ensure_one()
        self.item_id.write({
            'odoo_instance_url': self.odoo_instance_url,
            'odoo_database': self.odoo_database,
            'odoo_login': self.odoo_login,
            'odoo_password': self.odoo_password,
        })
        return self.item_id.sync_with_odoo_instance()
