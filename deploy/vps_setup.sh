#!/bin/bash
# ==============================================================================
# JARVIS VPS Automated Deployment & Provisioning Script (Ubuntu/Debian)
# ==============================================================================
set -e

echo "======================================================================"
echo "      ⚡ JARVIS MARK-VII LINUX VPS AUTOMATED DEPLOYMENT SETUP ⚡      "
echo "======================================================================"

APP_DIR="/root/jarvis_bot"

# 1. Update OS and install system dependencies
echo "[1/5] Updating package cache and installing prerequisites..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv sqlite3 curl git

# 2. Prepare Application Directory
echo "[2/5] Setting up directory structures..."
mkdir -p "$APP_DIR/data"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/scripts"
mkdir -p /var/log

# 3. Install Python Dependencies
echo "[3/5] Installing Python dependencies..."
python3 -m pip install --upgrade pip
if [ -f "$APP_DIR/requirements.txt" ]; then
    python3 -m pip install -r "$APP_DIR/requirements.txt"
fi

# 4. Configure & Enable Systemd Service Daemon
echo "[4/5] Provisioning systemd daemon service..."
cp "$APP_DIR/deploy/jarvis.service" /etc/systemd/system/jarvis.service
chmod 644 /etc/systemd/system/jarvis.service
systemctl daemon-reload
systemctl enable jarvis.service
systemctl restart jarvis.service

# 5. Configure Automated Maintenance Crontab
echo "[5/5] Installing automated maintenance crontab..."
chmod +x "$APP_DIR/scripts/db_maintenance.sh"
crontab "$APP_DIR/deploy/crontab.txt"

echo "======================================================================"
echo "[SUCCESS] JARVIS Service Active and Deployed!"
echo "Check live status: systemctl status jarvis.service"
echo "Check live logs:   journalctl -u jarvis.service -f"
echo "======================================================================"
