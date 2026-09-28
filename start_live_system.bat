@echo off
title XAUUSD AI Trading Bot - Live Institutional Supervisor
color 0A

echo ======================================================================
echo       XAUUSD AI TRADING BOT - LIVE INSTITUTIONAL SUPERVISOR
echo ======================================================================
echo [SYSTEM] Initializing 24/5 Automated Execution Environment...

:: 1. Check MetaTrader 5 Terminal Process
tasklist /FI "IMAGENAME eq terminal64.exe" 2>NUL | find /I /N "terminal64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MetaTrader 5 terminal is running.
) else (
    echo [STARTING] MetaTrader 5 terminal not detected. Launching terminal...
    if exist "C:\Program Files\MetaTrader 5\terminal64.exe" (
        start "" "C:\Program Files\MetaTrader 5\terminal64.exe"
        timeout /t 5 >nul
    ) else (
        echo [WARNING] Could not locate default MT5 path. Please ensure MT5 is open manually.
    )
)

:: 2. Check & Start Central Licensing & Entitlement Server (:8000)
netstat -ano | find "8000" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Licensing & Entitlement Server is active on port 8000.
) else (
    echo [STARTING] Launching Licensing & Webhook Server on port 8000...
    start "XAUUSD Licensing Server" /B python licensing/server.py
    timeout /t 2 >nul
)

:: 3. Start Heartbeat Watchdog Daemon
echo [STARTING] Launching Standalone Heartbeat Watchdog Daemon...
start "XAUUSD Watchdog Daemon" /B python telemetry/watchdog.py

:: 4. Master Bot Execution Loop with Automatic Crash Recovery
:bot_supervisor_loop
echo ======================================================================
echo [SUPERVISOR] Starting Master AI Trading Bot Engine (PID: %RANDOM%)...
echo ======================================================================
python main.py

set EXIT_CODE=%ERRORLEVEL%
echo.
echo ======================================================================
echo [ALERT] Bot process terminated with exit code %EXIT_CODE% at %DATE% %TIME%
echo [AUTO-RECOVERY] Relaunching in 5 seconds... Press Ctrl+C to abort.
echo ======================================================================
timeout /t 5 >nul
goto bot_supervisor_loop
