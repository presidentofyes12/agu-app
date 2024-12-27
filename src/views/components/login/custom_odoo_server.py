#!/usr/bin/env python3
import sys
import os

# Add Odoo to Python path
odoo_path = '/opt/odoo/odoo'
sys.path.append(odoo_path)

import odoo
from odoo.tools import config
from nostr_auth import authenticate_user

if __name__ == "__main__":
    config.parse_config(sys.argv[1:])
    
    if config.get('auth_method') == 'nostr':
        def check_security(method, *args, **kwargs):
            # Get Nostr public and private keys from request
            public_key = odoo.http.request.params.get('public_key')
            private_key = odoo.http.request.params.get('private_key')
            
            if not public_key or not private_key:
                raise odoo.exceptions.AccessDenied()
            
            user_id = authenticate_user(public_key, private_key)
            if user_id:
                odoo.http.request.uid = user_id
            else:
                raise odoo.exceptions.AccessDenied()
        
        # Patch the root instance instead of the class
        odoo.http.root.check_security = check_security
    
    odoo.cli.main()
