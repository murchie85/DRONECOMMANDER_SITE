#!/bin/bash
# Backup Drone Commander site to a dated zip in the parent directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="../DRONECOMMANDER_SITE_backup_${TIMESTAMP}.zip"
zip -r "$FILENAME" . -x ".git/*" "instance/*" "__pycache__/*" "*.pyc" ".claude/*"
echo "Backup created: $FILENAME"
