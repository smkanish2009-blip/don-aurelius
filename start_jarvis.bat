@echo off
cd /d "%~dp0"
chcp 65001 >nul
title JARVIS Mark-VII Autonomous Trading Matrix
color 0B

echo ======================================================================
echo       [+] JARVIS MARK-VII QUANTUM AUTONOMOUS ALGORITHMIC MATRIX [+]
echo ======================================================================
echo [SYSTEM] Booting JARVIS Neural Intermarket and Voice Synthesis Stack...
echo.

:: 1. Verify MetaTrader 5 Terminal Process
tasklist /FI "IMAGENAME eq terminal64.exe" 2>NUL | find /I /N "terminal64.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MetaTrader 5 terminal profile detected and connected.
) else (
    echo [LAUNCH] MetaTrader 5 terminal not detected. Initializing terminal...
    if exist "C:\Program Files\MetaTrader 5\terminal64.exe" (
        start "" "C:\Program Files\MetaTrader 5\terminal64.exe"
        ping 127.0.0.1 -n 6 >nul
    ) else (
        echo [NOTICE] Terminal path custom. Assuming background MT5 instance.
    )
)

:: 2. Check Background Licensing & Entitlement Server (:8000)
netstat -ano | find "8000" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [OK] Central Licensing Server verified on port 8000.
) else (
    echo [LAUNCH] Booting Central Licensing Server on port 8000...
    start "JARVIS Licensing Core" /B python licensing/server.py
    ping 127.0.0.1 -n 3 >nul
)

:: 3. Continuous Execution Supervisor Loop
:jarvis_supervisor_loop
echo ======================================================================
echo [CORE] Initializing JARVIS Orchestration Engine...
echo ======================================================================
python run_jarvis.py

set EXIT_CODE=%ERRORLEVEL%
echo.
echo ======================================================================
echo [ALERT] JARVIS Core process exited with code %EXIT_CODE% at %DATE% %TIME%
echo [AUTO-RECOVERY] Relaunching in 5 seconds... Press Ctrl+C to terminate.
echo ======================================================================
ping 127.0.0.1 -n 6 >nul
goto jarvis_supervisor_loop
