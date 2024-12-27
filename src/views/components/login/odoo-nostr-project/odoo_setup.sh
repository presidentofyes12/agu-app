#!/bin/bash
# Add this near the top of your script, after the shebang line
set -Ee  # Exit on error
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

# And add these helper functions
cleanup() {
    local exit_code=$?
    log "Script exiting with code $exit_code"
    if [ $exit_code -ne 0 ]; then
        log "Showing last 50 lines of Odoo logs:"
        sudo docker logs --tail 50 odoo-nostr-project_odoo_1 || true
    fi
    exit $exit_code
}

trap cleanup EXIT

# Set environment variables with Nostr credentials
export NOSTR_PUBKEY="npub1qpr5ntstknpz6z9ar996c54m7uzs6mn0pf3yx537ymy0edjl4taqrx0z0q"
export NOSTR_PRIVKEY="nsec1lh24ln2m93xf9a7a4q3a32s5vu9kaj6n9je7uu00yhtgtea9wq2sxr3jxs"
export NOSTR_RELAYS="wss://nostr-pub.wellorder.net"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

initialize_base_module() {
    log "Starting base module initialization..."
    local max_attempts=3
    local attempt=1
    local success=false

    # First verify the database connection
    if ! sudo docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb -c "\dt" > /dev/null 2>&1; then
        log "Error: Cannot connect to database. Checking database status..."
        sudo docker exec -i odoo-nostr-project_postgres_1 psql -U postgres -c "\l"
        return 1
    fi

    # Verify Odoo container is running
    if ! sudo docker ps | grep -q odoo-nostr-project_odoo_1; then
        log "Error: Odoo container is not running!"
        return 1
    fi

    while [ $attempt -le $max_attempts ] && [ "$success" = false ]; do
        log "Attempt $attempt of $max_attempts..."
        
        # Check container status before attempting
        log "Container status:"
        sudo docker ps | grep odoo

        # Check Odoo logs before attempt
        log "Current Odoo logs:"
        sudo docker logs --tail 10 odoo-nostr-project_odoo_1
        
        log "Executing base module initialization..."
        # Run with verbose output and remove --no-http flag
        if sudo docker exec -i odoo-nostr-project_odoo_1 /opt/odoo/odoo/odoo-bin \
            -c /etc/odoo/odoo.conf \
            -d odoodb \
            -i base \
            --stop-after-init \
            --without-demo=all \
            --load-language=en_US \
            --log-level=debug; then
            
            success=true
            log "Base module initialization appears successful"
        else
            local exit_code=$?
            log "Initialization failed with exit code: $exit_code"
            
            # Get detailed logs
            log "Recent Odoo logs:"
            sudo docker logs --tail 50 odoo-nostr-project_odoo_1
            
            # Check database state
            log "Checking database state..."
            sudo docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb -c "SELECT name, state FROM ir_module_module WHERE name='base';"
            
            attempt=$((attempt + 1))
            if [ $attempt -le $max_attempts ]; then
                log "Waiting 10 seconds before next attempt..."
                sleep 10
            fi
        fi
    done

    if [ "$success" = false ]; then
        log "Failed to initialize base module after $max_attempts attempts"
        return 1
    fi

    return 0
}

# Function to wait for PostgreSQL
wait_for_postgres() {
    local retries=30
    local count=0
    until sudo docker exec odoo-nostr-project_postgres_1 pg_isready -h localhost -U postgres || [ $count -eq $retries ]; do
        log "Waiting for PostgreSQL to be ready... ($count/$retries)"
        sleep 2
        count=$((count + 1))
    done
    if [ $count -eq $retries ]; then
        log "Error: PostgreSQL did not become ready in time"
        exit 1
    fi
}

# Function to wait for database setup
wait_for_database() {
    local retries=30
    local count=0
    until sudo docker exec odoo-nostr-project_postgres_1 psql -U postgres -d odoodb -c "\q" 2>/dev/null || [ $count -eq $retries ]; do
        log "Waiting for database 'odoodb' to be ready... ($count/$retries)"
        sleep 2
        count=$((count + 1))
    done
    if [ $count -eq $retries ]; then
        log "Error: Database 'odoodb' did not become ready in time"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    log "Setting up PostgreSQL database..."
    sudo docker exec -i odoo-nostr-project_postgres_1 psql -U postgres << EOF
-- Create odoo user with password
DROP ROLE IF EXISTS odoo;
CREATE ROLE odoo WITH LOGIN SUPERUSER PASSWORD 'odoo';

-- Create database if it doesn't exist
DROP DATABASE IF EXISTS odoodb;
CREATE DATABASE odoodb OWNER odoo;

-- Connect to the database
\c odoodb

-- Create extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Set session parameters to avoid serialization failures
SET SESSION synchronous_commit = 'off';
SET default_transaction_isolation = 'read committed';
EOF
}

# Function to wait for Odoo
wait_for_odoo() {
    local retries=30
    local count=0
    until curl -s http://localhost:8069 >/dev/null || [ $count -eq $retries ]; do
        log "Waiting for Odoo to start... ($count/$retries)"
        sleep 2
        count=$((count + 1))
    done
    if [ $count -eq $retries ]; then
        log "Error: Odoo did not start in time"
        exit 1
    fi
}

# Cleanup
log "Cleaning up existing containers..."
sudo docker-compose down -v
sudo docker system prune -a --volumes -f

# Create required directories
log "Creating required directories..."
sudo mkdir -p /var/run/postgresql logs /var/log/odoo
sudo chmod -R 777 /var/run/postgresql logs /var/log/odoo

# Configure Odoo
log "Configuring Odoo..."
cat > odoo.conf << EOL
[options]
admin_passwd = admin
db_host = postgres
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoodb
addons_path = /opt/odoo/odoo/addons,/opt/odoo/odoo/odoo/addons,/opt/odoo/custom_addons
http_port = 8069
logfile = /var/log/odoo/odoo-server.log
log_level = debug
log_handler = [':DEBUG']
workers = 0
max_cron_threads = 1
proxy_mode = True
without_demo = True
dev_mode = False
EOL

# Start PostgreSQL
log "Starting PostgreSQL..."
sudo docker-compose up -d postgres
wait_for_postgres

# Setup database
setup_database
wait_for_database

# Start Odoo with host mapping
log "Starting Odoo with host mapping..."
sudo docker-compose up -d odoo

# --add-host=host.docker.internal:host-gateway

sleep 30

#wait_for_odoo

# Initialize base database
log "Initializing base module..."

#sudo docker exec -i odoo-nostr-project_odoo_1 /opt/odoo/odoo/odoo-bin \
#    -c /etc/odoo/odoo.conf \
#    -d odoodb \
#    -i base \
#    --stop-after-init \
#    --without-demo=all \
#   --no-http \
#    --load-language=en_US

{
    # Initialize base module with error handling
    if initialize_base_module; then
        log "Base module initialization completed successfully"
    else
        log "Base module initialization failed"
        exit 1
    fi

    # Continue with rest of script...
    log "Proceeding with Nostr schema setup..."
} 2>&1 | tee odoo_setup.log

# log "Base initialization complete, proceeding with Nostr schema setup..."

sleep 10

# Set up Nostr schema
log "Setting up Nostr schema..."
sudo docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb << 'EOF'
BEGIN;
ALTER TABLE res_users ADD COLUMN IF NOT EXISTS nostr_public_key VARCHAR;
ALTER TABLE res_users ADD COLUMN IF NOT EXISTS nostr_private_key VARCHAR;
ALTER TABLE res_users ADD COLUMN IF NOT EXISTS password_crypt VARCHAR;

DROP INDEX IF EXISTS nostr_public_key_unique;
CREATE UNIQUE INDEX nostr_public_key_unique ON res_users (nostr_public_key) WHERE nostr_public_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS nostr_relay (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS res_users_nostr_relay_rel (
    user_id INTEGER REFERENCES res_users(id) ON DELETE CASCADE,
    relay_id INTEGER REFERENCES nostr_relay(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, relay_id)
);
COMMIT;
EOF

# Generate and set admin password
log "Setting up admin user..."
HASHED_PASSWORD=$(sudo docker exec odoo-nostr-project_odoo_1 python3 -c "
from passlib.context import CryptContext;
ctx = CryptContext(schemes=['pbkdf2_sha512']);
print(ctx.hash('${NOSTR_PRIVKEY}'))")

sudo docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb << EOF
BEGIN;
UPDATE res_users 
SET login = '${NOSTR_PUBKEY}',
    password = '${HASHED_PASSWORD}',
    nostr_public_key = '${NOSTR_PUBKEY}',
    nostr_private_key = '${NOSTR_PRIVKEY}',
    active = true
WHERE id = 1;

UPDATE res_partner 
SET name = 'Nostr Admin', 
    email = '${NOSTR_PUBKEY}' 
WHERE id = 1;

INSERT INTO nostr_relay (name, url, is_active)
VALUES ('Default Relay', '${NOSTR_RELAYS}', true)
ON CONFLICT (url) DO NOTHING;

INSERT INTO res_users_nostr_relay_rel (user_id, relay_id)
SELECT 1, id FROM nostr_relay WHERE url = '${NOSTR_RELAYS}'
ON CONFLICT DO NOTHING;
COMMIT;
EOF

# Restart Odoo to apply changes
log "Restarting Odoo..."
sudo docker-compose restart odoo
sleep 10

# Verify setup
log "Verifying setup..."
sudo docker exec -i odoo-nostr-project_postgres_1 psql -U odoo -d odoodb << 'EOF'
\d res_users
SELECT login, active FROM res_users WHERE id = 1;
SELECT * FROM nostr_relay;
SELECT * FROM res_users_nostr_relay_rel;
EOF

log "Setup complete!"
log "Admin username (Nostr public key): $NOSTR_PUBKEY"
log "Admin password (Nostr private key): $NOSTR_PRIVKEY"
log "You can now access Odoo at http://localhost:8069"
