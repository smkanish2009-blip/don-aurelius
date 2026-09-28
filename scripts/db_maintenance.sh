#!/bin/bash
# Path: /root/jarvis_bot/scripts/db_maintenance.sh
# Automated Jarvis SQLite Database Maintenance Script
# Clears telemetry older than 30 days, VACUUMs and ANALYZEs database.

DB_PATH="/root/jarvis_bot/data/jarvis_metrics.db"
LOG_FILE="/var/log/jarvis_cron.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] Launching Automated Jarvis Database Maintenance..." >> "$LOG_FILE"

if [ -f "$DB_PATH" ]; then
    # Clear raw tracking telemetry older than 30 days to free up disk space
    sqlite3 "$DB_PATH" "DELETE FROM telemetry_logs WHERE timestamp <= datetime('now', '-30 days');"
    
    # Compress database storage allocation parameters
    sqlite3 "$DB_PATH" "VACUUM;"
    
    # Optimize index mapping layouts for query planner
    sqlite3 "$DB_PATH" "ANALYZE;"
    
    echo "[$(date)] Maintenance complete. Database structures optimized." >> "$LOG_FILE"
else
    echo "[$(date)] Notice: Database file not found at $DB_PATH." >> "$LOG_FILE"
fi
