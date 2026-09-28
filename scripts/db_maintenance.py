"""
Cross-Platform JARVIS Database Maintenance Utility.
Safely purges telemetry older than 30 days, VACUUMs pages, and runs ANALYZE.
Works on Windows, Linux, and macOS.
"""

import sys
import logging
from database.jarvis_logger import JarvisDatabaseLogger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [JarvisMaintenance]: %(message)s"
)
logger = logging.getLogger("JarvisMaintenance")


def main():
    logger.info("Executing automated database maintenance protocol...")
    db = JarvisDatabaseLogger()
    result = db.run_maintenance(retention_days=30)
    logger.info(f"Maintenance completed successfully: {result}")
    print(f"[OK] Database optimized. Cleared {result.get('deleted_telemetry_rows', 0)} telemetry records.")


if __name__ == "__main__":
    main()
