"""from odoo import models, fields, api
from nostr.key import PrivateKey

class ResUsers(models.Model):
    _inherit = 'res.users'

    #nostr_private_key = fields.Char(string="Nostr Private Key")
    #nostr_public_key = fields.Char(string="Nostr Public Key", compute='_compute_public_key')
    #nostr_relay_url = fields.Char(string="Nostr Relay URL")

    nostr_public_key = fields.Char(string="Nostr Public Key")
    nostr_private_key = fields.Char(string="Nostr Private Key")
    nostr_relay_url = fields.Char(string="Nostr Relay URL")

    @api.model
    def create(self, vals):
        if not vals.get('nostr_private_key'):
            private_key = PrivateKey()
            vals['nostr_private_key'] = private_key.bech32()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        # Here you might want to handle updates to Nostr fields
        return super(ResUsers, self).write(vals)

    @api.depends('nostr_private_key')
    def _compute_public_key(self):
        for user in self:
            if user.nostr_private_key:
                private_key = PrivateKey.from_nsec(user.nostr_private_key)
                user.nostr_public_key = private_key.public_key.bech32()
            else:
                user.nostr_public_key = False
"""

"""from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string="Nostr Public Key")
    nostr_private_key = fields.Char(string="Nostr Private Key")
    nostr_relay_url = fields.Char(string="Nostr Relay URL")

    @api.model
    def create(self, vals):
        # Here you might want to generate Nostr keys if they're not provided
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        # Here you might want to handle updates to Nostr fields
        return super(ResUsers, self).write(vals)"""
        
        
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string="Nostr Public Key")
    nostr_private_key = fields.Char(string="Nostr Private Key")
    nostr_relay_url = fields.Char(string="Nostr Relay URL")
