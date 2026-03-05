#!/bin/bash
# VPS Integration API - Deployment Script

set -e

INSTALL_DIR="/opt/vps-integration-api"

echo "====================================="
echo "VPS Integration API - Deploy"
echo "====================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Navigate to installation directory
cd $INSTALL_DIR || exit 1

# Pull latest changes
echo "Pulling latest changes..."
git pull

# Rebuild Docker image
echo "Building Docker image..."
docker build -t vps-integration-api:latest .

# Restart service
echo "Restarting service..."
systemctl restart vps-integration-api

# Wait for service to be ready
echo "Waiting for service to start..."
sleep 5

# Check service status
if systemctl is-active --quiet vps-integration-api; then
    echo "✓ Service is running"
else
    echo "✗ Service failed to start"
    echo "Check logs: journalctl -u vps-integration-api -n 50"
    exit 1
fi

# Test health endpoint
echo "Testing health endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

echo ""
echo "====================================="
echo "Deployment Complete!"
echo "====================================="
echo ""
echo "Service status: systemctl status vps-integration-api"
echo "View logs: journalctl -u vps-integration-api -f"
echo ""
