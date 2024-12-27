#!/bin/bash

PUBLIC_KEY=$1
PRIVATE_KEY=$2

if [ -z "$PUBLIC_KEY" ] || [ -z "$PRIVATE_KEY" ]; then
    echo "Usage: $0 <public_key> <private_key>"
    exit 1
fi

update_odoo_conf() {
    local config_file=$1
    local temp_file=$(mktemp)

    while IFS= read -r line; do
        case "$line" in
            db_user*)
                echo "db_user = $PUBLIC_KEY" >> "$temp_file"
                ;;
            db_password*)
                echo "db_password = $PRIVATE_KEY" >> "$temp_file"
                ;;
            admin_passwd*)
                echo "admin_passwd = $PRIVATE_KEY" >> "$temp_file"
                ;;
            *)
                echo "$line" >> "$temp_file"
                ;;
        esac
    done < "$config_file"

    sudo mv "$temp_file" "$config_file"
    sudo chown root:root "$config_file"
    sudo chmod 644 "$config_file"
}

# Update both odoo.conf files
update_odoo_conf "/etc/odoo/odoo.conf"
update_odoo_conf "./odoo.conf"

# Start PostgreSQL
sudo podman run -d --name postgres --pod odoo-pod \
  -e POSTGRES_USER="$PUBLIC_KEY" \
  -e POSTGRES_PASSWORD="$PRIVATE_KEY" \
  -e POSTGRES_DB=odoodb \
  -v pgdata:/var/lib/postgresql/data \
  postgres:14

# Start Odoo container
sudo podman run -d --name odoo-openeducat --pod odoo-pod \
  -v odoo-data:/opt/odoo/.local/share/Odoo \
  -v /etc/odoo/odoo.conf:/etc/odoo/odoo.conf:ro \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_USER="$PUBLIC_KEY" \
  -e DB_PASSWORD="$PRIVATE_KEY" \
  -e DB_NAME=odoodb \
  localhost/odoo-openeducat:latest \
  -i base --log-level=debug

echo "Odoo and PostgreSQL containers started."
