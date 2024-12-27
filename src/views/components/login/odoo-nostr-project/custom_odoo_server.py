#!/usr/bin/env python3
import sys
import os

# Add Odoo to Python path
odoo_path = '/opt/odoo/odoo'
sys.path.append(odoo_path)

import odoo
from odoo.tools import config
from odoo.exceptions import AccessDenied

if __name__ == "__main__":
    config.parse_config(sys.argv[1:])
    
    if config.get('auth_method') == 'nostr':
        def check_security(method, *args, **kwargs):
            if odoo.http.request and odoo.http.request.params:
                public_key = odoo.http.request.params.get('public_key')
                signature = odoo.http.request.params.get('signature')
                message = odoo.http.request.params.get('message')
                
                if public_key and signature and message:
                    user_id = odoo.http.request.env['res.users'].sudo().authenticate_nostr(public_key, signature, message)
                    if user_id:
                        odoo.http.request.uid = user_id
                        return
            
            return method(*args, **kwargs)

        odoo.http.Root.check_security = check_security

    # Force database initialization
    db_name = config['db_name']
    if not odoo.service.db.exp_db_exist(db_name):
        odoo.service.db.exp_create_database(
            db_name,
            demo=False,
            lang='en_US',
            user_password='admin'
        )
        print(f"Database '{db_name}' created.")
    else:
        print(f"Database '{db_name}' already exists.")

    # Initialize the database with base module
    odoo.modules.registry.Registry.new(db_name, update_module=True)
    
    odoo.cli.main()
