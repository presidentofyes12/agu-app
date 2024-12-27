#!/usr/bin/env python3
import sys
import os

# Add Odoo to Python path
odoo_path = '/opt/odoo/odoo'
sys.path.append(odoo_path)

import odoo
from odoo.tools import config
# from nostr_auth import authenticate_user

def authenticate_user(public_key, private_key):
    # Generate a random challenge
    challenge = os.urandom(32).hex()
    
    # Sign the challenge with the private key
    private_key_int = int(private_key, 16)
    private_key_obj = ec.derive_private_key(private_key_int, ec.SECP256K1())
    signature = private_key_obj.sign(challenge.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
    
    # Verify the signature
    if verify_nostr_signature(public_key, challenge, signature.hex()):
        # Check if user exists in Odoo database
        conn = psycopg2.connect(
            dbname="odoodb",
            user="odoo",
            password="your_secure_password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT id FROM res_users WHERE login = %s", (public_key,))
        user = cur.fetchone()
        
        if user:
            return user[0]  # Return user ID if exists
        else:
            # Create new user
            cur.execute("INSERT INTO res_users (login, password) VALUES (%s, %s) RETURNING id", (public_key, hashlib.sha256(private_key.encode()).hexdigest()))
            new_user_id = cur.fetchone()[0]
            conn.commit()
            return new_user_id
    else:
        return None

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
        
        odoo.http.root.check_security = check_security
    
    odoo.cli.main()
