#!/bin/bash
# === reset_admin.sh ===

set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Hardcoded Nostr keys
NOSTR_PUBKEY="npub1qpr5ntstknpz6z9ar996c54m7uzs6mn0pf3yx537ymy0edjl4taqrx0z0q"
NOSTR_PRIVKEY="nsec1lh24ln2m93xf9a7a4q3a32s5vu9kaj6n9je7uu00yhtgtea9wq2sxr3jxs"

log "Resetting admin to use Nostr authentication..."
docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb << EOF
-- Update admin user to use Nostr keys
UPDATE res_users 
SET login = '${NOSTR_PUBKEY}',
    password = '${NOSTR_PRIVKEY}',
    nostr_public_key = '${NOSTR_PUBKEY}',
    nostr_private_key = '${NOSTR_PRIVKEY}'
WHERE id = 1;

-- Ensure Nostr configuration is set
INSERT INTO ir_config_parameter (key, value)
VALUES 
    ('auth_provider', 'nostr'),
    ('nostr_authentication.enabled', 'true'),
    ('auth_nostr.enabled', 'true'),
    ('nostr.relay_urls', 'wss://nostr-pub.wellorder.net')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Ensure relay URLs are set
INSERT INTO nostr_relay_urls (url, is_active)
VALUES 
    ('wss://nostr-pub.wellorder.net', true)
ON CONFLICT (url) DO UPDATE SET is_active = true;
EOF

log "Restarting Odoo to apply changes..."
docker-compose restart odoo

log "Reset complete!"
log "You can now login with:"
log "Username (Public Key): $NOSTR_PUBKEY"
log "Password (Private Key): $NOSTR_PRIVKEY"
