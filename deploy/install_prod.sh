#!/bin/bash

# Prompt Manager Install Script for Production
# Run as: sudo bash install_prod.sh [port]

set -e

NGINX_PORT=${1:-8080}
APP_USER="prompt"
APP_HOME="/opt/prompt_manager"
UPLOAD_DIR="/var/lib/prompt_manager/uploads"
BACKUP_DIR="/var/backups/prompt_manager"

echo "=== Prompt Manager Installation ==="
echo "Nginx port: $NGINX_PORT"

# Create directories
echo "Creating directories..."
sudo mkdir -p "$APP_HOME"
sudo mkdir -p "$UPLOAD_DIR"
sudo mkdir -p "$BACKUP_DIR"

# Create user
echo "Creating user..."
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd -r -s /bin/false "$APP_USER"
fi

sudo chown -R "$APP_USER":"$APP_USER" "$APP_HOME"
sudo chown -R "$APP_USER":"$APP_USER" "$UPLOAD_DIR"
sudo chown -R "$APP_USER":"$APP_USER" "$BACKUP_DIR"

# Create systemd service
echo "Setting up systemd service..."
sudo cat > /etc/systemd/system/prompt_manager.service << EOF
[Unit]
Description=Prompt Manager System
After=network.target postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_HOME
Environment="PATH=$APP_HOME/venv/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="NGINX_PORT=$NGINX_PORT"
ExecStart=$APP_HOME/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
echo "Setting up nginx..."
sudo cat > /etc/nginx/sites-available/prompt_manager << EOF
server {
    listen $NGINX_PORT;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static {
        alias $APP_HOME/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias $UPLOAD_DIR;
        expires 7d;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/prompt_manager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Check nginx configuration
echo "Checking nginx configuration..."
if ! sudo nginx -t 2>&1; then
    echo "Nginx config error!"
    exit 1
fi

# Reload systemd and services
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "=== Installation complete ==="
echo "Nginx port: $NGINX_PORT"
echo "To start the service: sudo systemctl start prompt_manager"
echo "To enable on boot: sudo systemctl enable prompt_manager"
echo "Reload nginx: sudo systemctl reload nginx"
