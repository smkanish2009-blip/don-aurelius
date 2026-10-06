@echo off
REM =====================================================================
REM DON AURELIUS SOVEREIGN SYNDICATE - 3-2-1 BACKUP RUNNER
REM Executes automated SQLite hot backup, SHA-256 verification, and offsite staging
REM =====================================================================

cd /d "%~dp0\.."
echo [INFO] Running Don Aurelius 3-2-1 Enterprise Backup Engine...
python scripts\backup_321_engine.py
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 3-2-1 Backup completed successfully with zero corruption.
) else (
    echo [ERROR] Backup execution failed with error code %ERRORLEVEL%.
)
