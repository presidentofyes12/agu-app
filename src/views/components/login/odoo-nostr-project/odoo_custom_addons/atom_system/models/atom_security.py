from odoo import models, fields, api
from cryptography.fernet import Fernet

class AtomSecurityGroup(models.Model):
    _name = 'atom.security.group'
    _description = 'Atom Security Group'

    name = fields.Char(string='Group Name', required=True)
    user_ids = fields.Many2many('res.users', string='Users')
    element_ids = fields.Many2many('atom.element', string='Accessible Elements')

class AtomElementValue(models.Model):
    _inherit = 'atom.element.value'

    encryption_key = fields.Char(string='Encryption Key')

    @api.model
    def create(self, vals):
        if vals.get('encryption_key'):
            fernet = Fernet(vals['encryption_key'].encode())
            for field in ['value1', 'value2', 'value3']:
                if vals.get(field):
                    vals[field] = fernet.encrypt(str(vals[field]).encode()).decode()
        return super(AtomElementValue, self).create(vals)

    def read(self, fields=None, load='_classic_read'):
        result = super(AtomElementValue, self).read(fields, load)
        for record in result:
            if record.get('encryption_key'):
                fernet = Fernet(record['encryption_key'].encode())
                for field in ['value1', 'value2', 'value3']:
                    if record.get(field):
                        record[field] = float(fernet.decrypt(record[field].encode()).decode())
        return result