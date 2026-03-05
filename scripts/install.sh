#!/bin/bash
# VPS Integration API - Installation Script
# Supports x86_64 and ARM64 (aarch64) architectures

set -e

echo "====================================="
echo "VPS Integration API - Installer"
echo "====================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [[ "$ARCH" != "x86_64" && "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo "Warning: Unsupported architecture. Supported: x86_64, aarch64, arm64"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Enable and start Docker
echo "Configuring Docker..."
systemctl enable docker
systemctl start docker

# Add current user to docker group (if not root)
if [ "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "Added $SUDO_USER to docker group"
fi

# Create installation directory
INSTALL_DIR="/opt/vps-integration-api"
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Clone repository if not already present
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    git clone https://github.com/jessiorg/vps-integration-api.git .
else
    echo "Repository already exists, pulling latest changes..."
    git pull
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/g" .env
    
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and configure:"
    echo "  - GITHUB_CLIENT_ID"
    echo "  - GITHUB_CLIENT_SECRET"
    echo "  - GITHUB_REDIRECT_URI"
    echo "  - ALLOWED_USERS"
    echo ""
    read -p "Press Enter to edit .env file now..." -n 1 -r
    nano .env
else
    echo ".env file already exists"
fi

# Build Docker image
echo "Building Docker image..."
docker build -t vps-integration-api:latest .

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/vps-integration-api.service <<EOF
[Unit]
Description=VPS Integration API
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStartPre=-/usr/bin/docker stop vps-integration-api
ExecStartPre=-/usr/bin/docker rm vps-integration-api
ExecStart=/usr/bin/docker run --rm --name vps-integration-api \\
    -p 8000:8000 \\
    -v /var/run/docker.sock:/var/run/docker.sock \\
    -v $INSTALL_DIR:/app \\
    --env-file $INSTALL_DIR/.env \\
    vps-integration-api:latest
ExecStop=/usr/bin/docker stop vps-integration-api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable vps-integration-api.service

# Configure Nginx reverse proxy
echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/vps-integration-api <<'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/vps-integration-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx

# Configure firewall
echo "Configuring firewall..."
ufw --force enable
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp

echo ""
echo "====================================="
echo "Installation Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Configure your .env file: nano $INSTALL_DIR/.env"
echo "2. Start the service: systemctl start vps-integration-api"
echo "3. Check status: systemctl status vps-integration-api"
echo "4. View logs: journalctl -u vps-integration-api -f"
echo "5. Set up SSL: certbot --nginx -d your-domain.com"
echo ""
echo "API will be available at: http://$(hostname -I | awk '{print $1}')"
echo "Documentation: http://$(hostname -I | awk '{print $1}')/docs"
echo ""
