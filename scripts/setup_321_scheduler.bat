@echo off
REM =====================================================================
REM DON AURELIUS SOVEREIGN SYNDICATE - 3-2-1 BACKUP SCHEDULER INSTALLER
REM Registers a daily Windows Task Scheduler job to run at 23:59 UTC / local
REM =====================================================================

set TASK_NAME=DonAurelius_321_Backup
set BATCH_PATH=%~dp0run_321_backup.bat

echo =====================================================================
echo  Don Aurelius Institutional 3-2-1 Backup Task Registration
echo =====================================================================
echo Target Batch Runner: %BATCH_PATH%
echo Target Schedule: Daily at 23:59 (Market Close Rollover)
echo.

schtasks /create /tn "%TASK_NAME%" /tr "\"%BATCH_PATH%\"" /sc daily /st 23:59 /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Windows Task '%TASK_NAME%' successfully registered!
    echo It will execute automatically every night at 23:59.
) else (
    echo.
    echo [WARNING] Could not register scheduled task automatically.
    echo If prompted, please run this script as Administrator.
)
pause
