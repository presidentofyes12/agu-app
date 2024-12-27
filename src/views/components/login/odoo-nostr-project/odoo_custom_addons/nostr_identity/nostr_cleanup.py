# nostr_identity/nostr_cleanup.py

import atexit
from odoo import api, SUPERUSER_ID

def cleanup_connections():
    try:
        with api.Environment.manage():
            env = api.Environment(odoo.registry(odoo.tools.config['db_name']).cursor(), SUPERUSER_ID, {})
            verifiers = env['nostr.identity.verifier'].search([])
            for verifier in verifiers:
                verifier.close_connection()
            env.cr.commit()
    except Exception as e:
        # Log the error, but don't raise it to avoid interfering with Odoo's shutdown process
        _logger.error(f"Error during Nostr connection cleanup: {e}")
    finally:
        if env and env.cr:
            env.cr.close()

atexit.register(cleanup_connections)
