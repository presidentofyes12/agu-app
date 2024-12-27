#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create logs directory if it doesn't exist
mkdir -p logs
chmod 777 logs

# Check Odoo logs
check_odoo_logs() {
    log "Checking Odoo logs..."
    sudo docker exec odoo-nostr-project_odoo_1 tail -n 100 /var/log/odoo/odoo-server.log
}

# Check database status
check_db_status() {
    log "Checking database status..."
    sudo docker exec odoo-nostr-project_postgres_1 psql -U odoo -d odoodb -c "\dt"
    sudo docker exec odoo-nostr-project_postgres_1 psql -U odoo -d odoodb -c "SELECT * FROM ir_module_module WHERE state = 'installed';"
    sudo docker exec odoo-nostr-project_postgres_1 psql -U odoo -d odoodb -c "SELECT login, password, nostr_public_key, active FROM res_users WHERE id = 1;"
}

# Check Python dependencies
check_python_deps() {
    log "Checking Python dependencies..."
    sudo docker exec odoo-nostr-project_odoo_1 pip3 freeze
}

# Check module status
check_module_status() {
    log "Checking module status..."
    sudo docker exec odoo-nostr-project_odoo_1 python3 -c "
from odoo.service.db import list_dbs
print('Available databases:', list_dbs())
"
}

# Print container logs
log "Printing Odoo container logs..."
sudo docker logs odoo-nostr-project_odoo_1

log "Printing Postgres container logs..."
sudo docker logs odoo-nostr-project_postgres_1

# Run checks
check_odoo_logs
check_db_status
check_python_deps
check_module_status

# Create a test user to verify authentication
log "Creating test user..."
sudo docker exec odoo-nostr-project_postgres_1 psql -U odoo -d odoodb << EOF
INSERT INTO res_users (login, password, nostr_public_key, nostr_private_key, active)
VALUES ('test@example.com', 'test123', 'npub1test', 'nsec1test', true)
ON CONFLICT (login) DO UPDATE
SET password = EXCLUDED.password,
    nostr_public_key = EXCLUDED.nostr_public_key,
    nostr_private_key = EXCLUDED.nostr_private_key,
    active = true;
EOF

log "Debug information collection complete. Check the logs directory for detailed output."
