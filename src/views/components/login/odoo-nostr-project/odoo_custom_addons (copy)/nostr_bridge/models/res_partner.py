from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    nostr_public_key = fields.Char(string="Nostr Public Key")
