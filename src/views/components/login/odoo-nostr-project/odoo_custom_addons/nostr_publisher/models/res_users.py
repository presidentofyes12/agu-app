from odoo import models, fields, api, _
from odoo.exceptions import UserError
from nostr.key import PrivateKey
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    nostr_public_key = fields.Char(string="Nostr Public Key")
    nostr_private_key = fields.Char(string="Nostr Private Key")

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if not user.nostr_public_key or not user.nostr_private_key:
            user._generate_nostr_keys()
        return user

    def _generate_nostr_keys(self):
        private_key, public_key = self.env['nostr.publisher']._generate_key_pair()
        self.write({
            'nostr_private_key': private_key,
            'nostr_public_key': public_key,
        })
        _logger.info(f"Generated new Nostr keys for user {self.name}")

    def action_reset_nostr_keys(self):
        self.ensure_one()
        self._generate_nostr_keys()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Nostr Keys Reset"),
                'message': _("New Nostr keys have been generated for this user."),
                'type': 'success',
            }
        }

    def get_nostr_public_key(self):
        self.ensure_one()
        if not self.nostr_public_key:
            raise UserError(_("Nostr public key not set for this user."))
        return self.nostr_public_key

    def get_nostr_private_key(self):
        self.ensure_one()
        if not self.nostr_private_key:
            raise UserError(_("Nostr private key not set for this user."))
        return self.nostr_private_key
