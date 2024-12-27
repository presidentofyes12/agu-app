#!/bin/bash

PUBLIC_KEY=$1
PRIVATE_KEY=$2

if [ -z "$PUBLIC_KEY" ] || [ -z "$PRIVATE_KEY" ]; then
    echo "Usage: $0 <public_key> <private_key>"
    exit 1
fi

# Start PostgreSQL
sudo podman run -d --name postgres \
  -e POSTGRES_USER="$PUBLIC_KEY" \
  -e POSTGRES_PASSWORD="$PRIVATE_KEY" \
  -e POSTGRES_DB=odoodb \
  -v pgdata:/var/lib/postgresql/data \
  postgres:14

# Get PostgreSQL container IP
POSTGRES_IP=$(sudo podman inspect -f '{{.NetworkSettings.IPAddress}}' postgres)

# Start Odoo container
sudo podman run -d --name odoo-openeducat \
  -p 8069:8069 -p 8071:8071 \
  -v odoo-data:/opt/odoo/.local/share/Odoo \
  -v /etc/odoo/odoo.conf:/etc/odoo/odoo.conf:ro \
  -e DB_HOST=$POSTGRES_IP \
  -e DB_PORT=5432 \
  -e DB_USER="$PUBLIC_KEY" \
  -e DB_PASSWORD="$PRIVATE_KEY" \
  -e DB_NAME=odoodb \
  localhost/odoo-openeducat:latest

echo "Odoo and PostgreSQL containers started."
