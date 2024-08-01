#!/bin/bash

# Run this script with sudo privileges

# Check if Nginx is installed
if ! command -v nginx &> /dev/null
then
    echo "Nginx not found. Installing Nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Backup the existing default configuration
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak

# Create a new Nginx configuration
cat > /etc/nginx/sites-available/default << EOF
server {
    listen 80;
    server_name _;  # Catches any domain name

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Test Nginx configuration
nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx configuration test successful."
    # Reload Nginx to apply changes
    systemctl reload nginx
    echo "Nginx reloaded. Port forwarding from 80 to 5000 is now active."
else
    echo "Nginx configuration test failed. Please check the configuration manually."
    # Restore the backup
    mv /etc/nginx/sites-available/default.bak /etc/nginx/sites-available/default
    echo "Original configuration restored."
fi

# Remind about firewall and security group
echo "Remember to update your firewall and AWS EC2 security group to allow inbound traffic on port 80."
