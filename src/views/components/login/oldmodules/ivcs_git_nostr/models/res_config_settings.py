from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ivcs_git_nostr_relay_urls = fields.Char(string="Nostr Relay URLs", config_parameter='ivcs_git_nostr.relay_urls')
    ivcs_git_nostr_log_level = fields.Selection([
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical')
    ], string="Log Level", default='INFO', config_parameter='ivcs_git_nostr.log_level')
    ivcs_git_nostr_git_timeout = fields.Integer(string="Git Operation Timeout (seconds)", default=30, config_parameter='ivcs_git_nostr.git_timeout')
