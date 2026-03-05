#!/bin/bash
# VPS Integration API - Backup Script

set -e

INSTALL_DIR="/opt/vps-integration-api"
BACKUP_DIR="/var/backups/vps-integration-api"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

echo "====================================="
echo "VPS Integration API - Backup"
echo "====================================="

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration and data
echo "Creating backup..."
tar -czf $BACKUP_FILE \
    -C $INSTALL_DIR \
    .env \
    docker-compose.yml \
    || true

echo "Backup created: $BACKUP_FILE"
echo "Size: $(du -h $BACKUP_FILE | cut -f1)"

# Keep only last 7 backups
echo "Cleaning old backups..."
ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup complete!"
