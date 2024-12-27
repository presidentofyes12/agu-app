#!/bin/bash

# Set the correct paths
PROJECT_PATH=~/oldhome/home/impromise/Downloads/Telegram\ Desktop/nostr-w-relay-main\ \(2\)/nostr-w-relay-main\ \(1\)/src/views/components/login/odoo-nostr-project
CUSTOM_ADDONS_PATH="$PROJECT_PATH/odoo_custom_addons"
QUEUE_PATH="$CUSTOM_ADDONS_PATH/queue"

# Navigate to the project directory
cd "$PROJECT_PATH"

# Update odoo.conf
ODOO_CONF="/etc/odoo/odoo.conf"

# Function to safely update addons_path in odoo.conf
update_addons_path() {
    if grep -q "^addons_path" "$ODOO_CONF"; then
        # If addons_path exists, append new paths
        sudo sed -i "/^addons_path/s|$|,$CUSTOM_ADDONS_PATH,$QUEUE_PATH|" "$ODOO_CONF"
    else
        # If addons_path doesn't exist, add it
        echo "addons_path = $CUSTOM_ADDONS_PATH,$QUEUE_PATH" | sudo tee -a "$ODOO_CONF"
    fi
}

# Update the addons_path
update_addons_path

# Update docker-compose.yml to mount the custom_addons directory
if ! grep -q "./odoo_custom_addons:/opt/odoo/custom_addons" docker-compose.yml; then
    sed -i '/volumes:/a\      - ./odoo_custom_addons:/opt/odoo/custom_addons' docker-compose.yml
fi

# Rebuild and restart Docker containers
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d

# Wait for containers to start
sleep 30

# Check container status
sudo docker ps

# Update module list
sudo docker exec -it odoo-nostr-project_odoo_1 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoodb --stop-after-init -u base

# Install queue_job module
sudo docker exec -it odoo-nostr-project_odoo_1 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoodb -i queue_job --stop-after-init

# Now update/install all other modules
modules=(
    "nostr_bridge" "nostr_auth" "ivcs_git_nostr" "nostr_identity" "atom_system"
    "decentralized_sync" "git_nostr_bridge" "git_branch_manager"
    "custom_thunderbird_mail" "simple_git_integration" "opinion_reputation_system"
    "gitlab_nostr_bridge" "nostr_publisher"
)

for module in "${modules[@]}"
do
    sudo docker exec -it odoo-nostr-project_odoo_1 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoodb -i $module --stop-after-init
done

# Check Odoo logs
sudo docker logs odoo-nostr-project_odoo_1

echo "Installation and update process completed. Please check Odoo logs for any errors."
