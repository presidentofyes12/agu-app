import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64

class NostrAuthModule(models.AbstractModel):
    _name = 'nostr.auth'
    _description = 'Nostr Authentication Module'

    @api.model
    def generate_keypair(self):
        """
        Generate a new Nostr keypair.
        This represents the 'Cause' in our 'Causal Relationship'.
        """
        private_key = ec.generate_private_key(ec.SECP256K1())
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': base64.b64encode(private_bytes).decode('utf-8'),
            'public_key': base64.b64encode(public_bytes).decode('utf-8')
        }

    @api.model
    def store_keys(self, user_id, public_key, private_key):
        """
        Store the Nostr keys for a user.
        This action creates an 'Effect' in our 'Causal Relationship'.
        """
        user = self.env['res.users'].browse(user_id)
        if not user.exists():
            raise ValidationError("User does not exist")
        
        user.write({
            'nostr_public_key': public_key,
            'nostr_private_key': private_key  # In a real-world scenario, encrypt this before storage
        })

    @api.model
    def verify_signature(self, public_key, message, signature):
        """
        Verify a Nostr signature.
        This verification process is another 'Effect' in our 'Causal Relationship'.
        """
        try:
            public_key_obj = serialization.load_pem_public_key(base64.b64decode(public_key))
            signature_bytes = base64.b64decode(signature)
            public_key_obj.verify(
                signature_bytes,
                message.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except:
            return False

    @api.model
    def authenticate_nostr(self, public_key, signature, message):
        """
        Authenticate a user using Nostr.
        This method embodies the complete 'Causal Relationship':
        The provided credentials (Cause) lead to authentication success or failure (Effect).
        """
        user = self.env['res.users'].search([('nostr_public_key', '=', public_key)], limit=1)
        if user and self.verify_signature(user.nostr_public_key, message, signature):
            return user.id
        return False

# For console testing
if __name__ == "__main__":
    # Simulate Odoo environment
    class MockEnv:
        def __init__(self):
            self.users = {}
        
        def __getitem__(self, key):
            return self
        
        def search(self, domain, limit=None):
            for user_id, user in self.users.items():
                if user['nostr_public_key'] == domain[0][2]:
                    return [MockUser(user_id, user)]
            return []
    
    class MockUser:
        def __init__(self, id, data):
            self.id = id
            self.__dict__.update(data)
        
        def exists(self):
            return True
        
        def write(self, vals):
            self.__dict__.update(vals)

    mock_env = MockEnv()
    
    # Create an instance of NostrAuthModule
    nostr_auth = NostrAuthModule()
    nostr_auth.env = mock_env

    # Test key generation
    print("Generating keypair...")
    keys = nostr_auth.generate_keypair()
    print(f"Public Key: {keys['public_key'][:32]}...")
    print(f"Private Key: {keys['private_key'][:32]}...")

    # Test key storage
    print("\nStoring keys...")
    mock_env.users[1] = {'name': 'Test User'}
    try:
        nostr_auth.store_keys(1, keys['public_key'], keys['private_key'])
        print("Keys stored successfully")
    except Exception as e:
        print(f"Error storing keys: {str(e)}")

    # Test signature verification
    print("\nTesting signature verification...")
    message = "Test message"
    private_key = serialization.load_pem_private_key(base64.b64decode(keys['private_key']), password=None)
    signature = base64.b64encode(private_key.sign(
        message.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )).decode('utf-8')
    
    is_valid = nostr_auth.verify_signature(keys['public_key'], message, signature)
    print(f"Signature valid: {is_valid}")

    # Test authentication
    print("\nTesting authentication...")
    user_id = nostr_auth.authenticate_nostr(keys['public_key'], signature, message)
    print(f"Authenticated user ID: {user_id}")

    print("\nAll tests completed.")
