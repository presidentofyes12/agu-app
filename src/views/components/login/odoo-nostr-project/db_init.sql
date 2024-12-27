-- Create the ir_config_parameter table if it doesn't exist
CREATE TABLE IF NOT EXISTS ir_config_parameter (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT
);

-- Create relay table if it doesn't exist
CREATE TABLE IF NOT EXISTS nostr_relay_urls (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add configuration parameters
INSERT INTO ir_config_parameter (key, value)
VALUES 
    ('auth_provider', 'nostr'),
    ('nostr_authentication.enabled', 'true'),
    ('auth_nostr.enabled', 'true'),
    ('nostr.relay_urls', 'wss://nostr-pub.wellorder.net')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Add relay URLs
INSERT INTO nostr_relay_urls (url, is_active)
VALUES 
    ('wss://nostr-pub.wellorder.net', true)
ON CONFLICT (url) DO UPDATE SET is_active = true;
