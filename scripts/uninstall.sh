#!/bin/bash
# VPS Integration API - Uninstall Script

set -e

INSTALL_DIR="/opt/vps-integration-api"

echo "====================================="
echo "VPS Integration API - Uninstall"
echo "====================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

read -p "Are you sure you want to uninstall? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Stop and disable service
echo "Stopping service..."
systemctl stop vps-integration-api || true
systemctl disable vps-integration-api || true

# Remove systemd service file
echo "Removing systemd service..."
rm -f /etc/systemd/system/vps-integration-api.service
systemctl daemon-reload

# Remove Docker container and image
echo "Removing Docker resources..."
docker stop vps-integration-api || true
docker rm vps-integration-api || true
docker rmi vps-integration-api:latest || true

# Remove Nginx configuration
echo "Removing Nginx configuration..."
rm -f /etc/nginx/sites-enabled/vps-integration-api
rm -f /etc/nginx/sites-available/vps-integration-api
systemctl restart nginx || true

# Ask about installation directory
read -p "Remove installation directory ($INSTALL_DIR)? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing installation directory..."
    rm -rf $INSTALL_DIR
else
    echo "Installation directory preserved: $INSTALL_DIR"
fi

echo ""
echo "====================================="
echo "Uninstall Complete!"
echo "====================================="
echo ""
