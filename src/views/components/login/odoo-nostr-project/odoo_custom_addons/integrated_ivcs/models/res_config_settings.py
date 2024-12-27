from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    integrated_ivcs_relay_urls = fields.Char(string="Nostr Relay URLs", config_parameter='integrated_ivcs.relay_urls')
