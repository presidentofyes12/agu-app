#!/bin/bash

set -e

# Add a small delay to ensure PostgreSQL is fully up
sleep 10

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Create the database if it doesn't exist
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -U $DB_USER $DB_NAME
fi

# Initialize the database with the admin user using the private key
python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d $DB_NAME -i base --stop-after-init --no-http \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --admin_passwd=$DB_PASSWORD

# Update the admin user's login and password
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "UPDATE res_users SET login = '$DB_USER', password = '$DB_PASSWORD' WHERE id = 1;"

# Start Odoo
exec /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --admin_passwd=$DB_PASSWORD \
    "$@"
