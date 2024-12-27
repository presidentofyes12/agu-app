#!/bin/bash

EMAIL=$1
NPUB=$2
NSEC=$3
ODOORESET=$4
GITLABRESET=$5

echo "Installing all dependencies:"
sleep 5
sudo npm install --force

if [ -z "$EMAIL" ]; then
    echo "Please input a valid email."
    read EMAIL
    # After getting email, check for keypair
    if [ -z "$NPUB" ] || [ -z "$NSEC" ]; then
        echo "Please input a Nostr keypair. Go to the Nostr app site to generate a new Nostr account with its keypair, cancel the execution of the site (ctrl-C in this terminal), and then input the new Nostr keypair."
        sleep 5
        sudo kill -9 $(sudo lsof -t -i:3000)
        sudo npm run start
        echo "Nostr public key:"
        read NPUB
        echo "Nostr secret key:"
        read NSEC
    fi
elif [ -z "$NPUB" ] || [ -z "$NSEC" ]; then
    echo "Please input a Nostr keypair. Go to the Nostr app site to generate a new Nostr account with its keypair, cancel the execution of the site (ctrl-C in this terminal), and then input the new Nostr keypair."
    sleep 5
    sudo kill -9 $(sudo lsof -t -i:3000)
    sudo npm run start
    echo "Nostr public key:"
    read NPUB
    echo "Nostr secret key:"
    read NSEC
fi

# Common setup sequence after all credentials are collected
echo "Starting setup with credentials..."
sleep 5
sudo kill -9 $(sudo lsof -t -i:3000)
sudo npm run start &
cd ../odoo-nostr-project/

if [ "$ODOORESET" = "reset" ]; then
    sudo ./odoo_setup.sh reset "$EMAIL" "$NPUB" "$NSEC"
else
    sudo ./odoo_setup.sh none "$EMAIL" "$NPUB" "$NSEC"
fi

if [ "$GITLABRESET" = "reset" ]; then
    sudo ./gitlab_setup.sh reset "$EMAIL" "$NPUB" "$NSEC" http://localhost:8080
else
    sudo ./gitlab_setup.sh none "$EMAIL" "$NPUB" "$NSEC" http://localhost:8080
fi

cd ..

cd agu-app

echo "Setting up server:"

sudo node ./src/views/components/relay/server.js &
