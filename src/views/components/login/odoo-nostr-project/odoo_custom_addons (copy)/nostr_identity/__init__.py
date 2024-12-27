# nostr_identity/__init__.py

from . import models
from . import nostr_cleanup

def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Generate encryption key if it doesn't exist
    if not env['ir.config_parameter'].get_param('nostr.encryption_key'):
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key()
        env['ir.config_parameter'].set_param('nostr.encryption_key', encryption_key.decode())

def uninstall_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Remove the encryption key
    env['ir.config_parameter'].set_param('nostr.encryption_key', False)
    
    # Close all active WebSocket connections
    verifiers = env['nostr.identity.verifier'].search([])
    for verifier in verifiers:
        verifier.close_connection()
