#!/bin/bash
set -e

# Modify the initialize_module function in docker-entrypoint.sh
initialize_module() {
    local module=$1
    echo "Initializing module: $module"
    python3 /opt/odoo/odoo/odoo-bin \
        -c /etc/odoo/odoo.conf \
        -d "$DB_NAME" \
        -i "$module" \
        --stop-after-init \
        --without-demo=all \
        --log-level=debug \
        2>&1 | tee /var/log/odoo/module_init_${module}.log || {
        echo "Error initializing module $module - check /var/log/odoo/module_init_${module}.log"
        cat /var/log/odoo/module_init_${module}.log
        return 1
    }
    echo "Module $module initialized successfully"
}

# Function to check if postgres is ready
postgres_ready() {
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "\q" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    return 1
}

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until postgres_ready; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Create database if it doesn't exist
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Ensure ir_config_parameter table exists
echo "Configuring database tables..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS ir_config_parameter (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT
);

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
EOF

# Initialize database if needed
python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d $DB_NAME -i base --stop-after-init || true

initialize_module "base"
initialize_module "web"
initialize_module "bus"
initialize_module "mail"

python3 /opt/odoo/fix_mail_setup.py

# run pre-update checks
if [ -f /opt/odoo/check_nostr_bridge.sh ]; then
    /opt/odoo/check_nostr_bridge.sh
fi
sleep 2

# Start Odoo
exec "$@"
