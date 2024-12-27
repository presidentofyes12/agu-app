#!/bin/bash
set -e  # Exit on error

echo "Setting environmental variables:"

# Environment variables
export GITLAB_EMAIL="nkenna@iheakaram.com"
export NOSTR_PUBKEY="npub1qpr5ntstknpz6z9ar996c54m7uzs6mn0pf3yx537ymy0edjl4taqrx0z0q"
export NOSTR_PRIVKEY="nsec1lh24ln2m93xf9a7a4q3a32s5vu9kaj6n9je7uu00yhtgtea9wq2sxr3jxs"
export GITLAB_URL="http://localhost:8080"
export RESET=$1

echo "Checking if they're set:"

# Check if variables are set
if [ -z "$GITLAB_EMAIL" ] || [ -z "$NOSTR_PUBKEY" ] || [ -z "$NOSTR_PRIVKEY" ]; then
    echo "Error: Required environment variables not set"
    exit 1
fi

# Debug output
echo "Starting script with RESET=${RESET}"

# Handle reset flag before any operations
if [ "$RESET" = "reset" ]; then
    echo "WARNING: This will RESET all of GitLab's current configurations!"
    echo "You have 10 seconds to cancel this operation (CTRL-C)"
    echo "Waiting..."
    sleep 10
    
    echo "Starting GitLab reset process..."
    
    # Stop GitLab first
    echo "Stopping GitLab services..."
    sudo gitlab-ctl stop || true
    
    echo "Cleaning up existing swap files..."
    if swapon --show | grep -q /swapfile2; then
        sudo swapoff /swapfile2 || true
    fi
    if [ -f /swapfile2 ]; then
        sudo rm -f /swapfile2 || true
    fi
    if swapon --show | grep -q /swapfile; then
        sudo swapoff /swapfile || true
    fi
    if [ -f /swapfile ]; then
        sudo rm -f /swapfile || true
    fi
    
    # Remove GitLab packages first
    echo "Removing GitLab packages..."
    sudo apt-get remove --purge -y gitlab-ce || true
    sudo apt-get remove --purge -y gitlab-ee || true
    sudo apt-get remove --purge -y gitlab-rails || true
    sudo apt-get remove --purge -y gitlab-rake || true
    sudo apt-get remove --purge -y gitlab-ctl || true
    
    # Remove GitLab directories
    echo "Removing GitLab directories..."
    sudo rm -rf /etc/gitlab || true
    sudo rm -rf /var/opt/gitlab || true
    sudo rm -rf /var/log/gitlab || true
    sudo rm -rf /opt/gitlab /var/cache/gitlab || true
    sudo rm -rf /etc/apt/sources.list.d/gitlab* || true
    
    # Clean up
    echo "Cleaning up..."
    sudo apt-get clean
    sudo apt-get autoremove -y
    sudo rm -rf /etc/sv/gitlab* /etc/service/gitlab*
    
    # Now try to set up swap
    echo "Setting up swap space..."
    sudo fallocate -l 2G /swapfile2 || echo "Failed to create swap file, continuing anyway..."
    if [ -f /swapfile2 ]; then
        sudo chmod 600 /swapfile2
        sudo mkswap /swapfile2
        sudo swapon /swapfile2
        sudo swapon --show
    fi
    
    # Add GitLab repository
    echo "Adding GitLab repository..."
    curl -fsSL https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | sudo bash
    sudo apt update
    
    echo "Reset complete. Continuing with fresh installation..."
    sleep 3

elif [ -z "$RESET" ]; then
    echo "You can run the program with the 'reset' flag to completely reset the GitLab configuration."
    echo "Usage: ./gitlab_setup.sh reset"
    sleep 10
else
    echo "Invalid flag provided. Program will execute as normal."
    sleep 10
fi
    
# Install required packages
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl git
sudo apt-get install -y postfix

# Install and configure GitLab
sudo GITLAB_ROOT_EMAIL="$GITLAB_EMAIL" GITLAB_ROOT_PASSWORD="$NOSTR_PRIVKEY" EXTERNAL_URL="$GITLAB_URL" apt install gitlab-ee

# Create user with proper namespace
echo "Creating user..."
sudo gitlab-rails runner "
begin
  # First create a namespace for the user
  namespace = Group.new(
    name: '${NOSTR_PUBKEY}',
    path: '${NOSTR_PUBKEY}'.downcase
  )
  
  if namespace.save
    puts 'Namespace created successfully'
    
    # Now create the user with the namespace
    user = User.new(
      username: '${NOSTR_PUBKEY}',
      email: '${GITLAB_EMAIL}',
      password: '${NOSTR_PRIVKEY}',
      password_confirmation: '${NOSTR_PRIVKEY}',
      name: '${NOSTR_PUBKEY}',  # Required field
      admin: false
    )
    user.skip_confirmation!
    
    if user.save
      puts 'User created successfully!'
      
      # Associate the user with the namespace
      namespace.add_owner(user)
      puts 'User associated with namespace'
    else
      puts 'Failed to create user:'
      puts user.errors.full_messages
    end
  else
    puts 'Failed to create namespace:'
    puts namespace.errors.full_messages
  end
rescue => e
  puts 'Error:'
  puts e.message
  puts e.backtrace
end"

# Configure GitLab
sudo gitlab-rake gitlab:check
sudo gitlab-ctl reconfigure

# Backup and update configuration
sudo cp /etc/gitlab/gitlab.rb /etc/gitlab/gitlab.rb.backup

# Update GitLab configuration
if ! grep -q "^external_url" /etc/gitlab/gitlab.rb; then
    echo -e "\nexternal_url 'http://localhost:8080'" | sudo tee -a /etc/gitlab/gitlab.rb
fi

# Configure Puma settings
if ! grep -q "^puma\['port'\]" /etc/gitlab/gitlab.rb; then
    echo -e "\n# Disable Puma from binding to a TCP port\npuma['port'] = nil" | sudo tee -a /etc/gitlab/gitlab.rb
fi
if ! grep -q "^puma\['listen'\]" /etc/gitlab/gitlab.rb; then
    echo -e "\n# Ensure Puma only binds to a Unix socket\npuma['listen'] = '/var/opt/gitlab/gitlab-rails/sockets/gitlab.socket'" | sudo tee -a /etc/gitlab/gitlab.rb
fi
if ! grep -q "^puma\['worker_processes'\]" /etc/gitlab/gitlab.rb; then
    echo -e "\n# Adjust the number of workers based on system resources\npuma['worker_processes'] = 2" | sudo tee -a /etc/gitlab/gitlab.rb
fi

# Display the changes
echo "Current configuration:"
echo "--------------------"
sudo grep -A 1 "external_url\|puma" /etc/gitlab/gitlab.rb

# Reconfigure and restart GitLab
echo -e "\nReconfiguring GitLab..."
sudo gitlab-ctl reconfigure
echo -e "\nRestarting GitLab..."
sudo gitlab-ctl restart

# Wait for GitLab to be ready
echo "Waiting for GitLab to be ready..."
until curl --output /dev/null --silent --head --fail "$GITLAB_URL"; do
    printf '.'
    sleep 10
done

# Create access token for Git operations
echo "Creating access token..."
token=$(sudo gitlab-rails runner "
begin
  # First make sure we can find the user
  user = User.find_by_username('${NOSTR_PUBKEY}')
  if user.nil?
    puts 'Error: User not found. Creating root token instead.'
    user = User.find_by_username('root')
  end

  # Create the token with explicit scope definitions
  scopes = ['api', 'read_user', 'read_repository', 'write_repository']
  
  # Delete any existing tokens with the same name
  PersonalAccessToken.where(user: user, name: 'Repository setup token').delete_all
  
  # Create new token
  token = PersonalAccessToken.create!(
    user: user,
    name: 'Repository setup token',
    scopes: scopes,
    expires_at: 1.year.from_now
  )
  
  if token.persisted?
    puts token.token
  else
    puts 'Failed to create token'
    exit 1
  end
rescue => e
  puts \"Error creating token: \#{e.message}\"
  exit 1
end")

# Verify token was created
if [ -z "$token" ]; then
    echo "Failed to get token from GitLab"
    exit 1
fi

# Test token works
echo "Testing token..."
response=$(curl --silent --header "PRIVATE-TOKEN: $token" "$GITLAB_URL/api/v4/user")
if [[ $response == *"message"*"Unauthorized"* ]]; then
    echo "Token authentication failed"
    exit 1
fi

echo "Token created successfully!"

# Set up Odoo repository
echo "Setting up Odoo repository..."
WORK_DIR=$(mktemp -d)
cd "$WORK_DIR" || exit 1

# Clone Odoo repository with retries
max_retries=3
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if git clone --depth=1 --branch=17.0 https://github.com/odoo/odoo.git; then
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Clone failed, retrying... ($retry_count/$max_retries)"
    sleep 5
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to clone repository after $max_retries attempts"
    exit 1
fi

cd odoo || exit 1

# Configure Git
git config --global user.email "$GITLAB_EMAIL"
git config --global user.name "$NOSTR_PUBKEY"

# Create new repository in GitLab via API with error handling
echo "Creating GitLab repository..."
create_response=$(curl --silent --header "PRIVATE-TOKEN: $token" \
     --data "name=odoo-nostr-project&visibility=private" \
     "$GITLAB_URL/api/v4/projects")

if [[ $create_response == *"error"* ]]; then
    echo "Failed to create repository: $create_response"
    exit 1
fi

# Push to GitLab with HTTP authentication
echo "Pushing to GitLab..."
git remote remove origin
git_url=$(echo "$GITLAB_URL" | sed 's|http://||')
git remote add origin "http://root:${NOSTR_PRIVKEY}@${git_url}/${NOSTR_PUBKEY}/odoo-nostr-project.git"

if ! git push -u origin --all; then
    echo "Failed to push to GitLab"
    exit 1
fi

# Cleanup
cd ..
rm -rf "$WORK_DIR"

# Display status and open GitLab
echo -e "\nChecking GitLab status..."
sudo gitlab-ctl status

echo "Setup complete! Opening GitLab..."
xdg-open "$GITLAB_URL"
