@echo off
chcp 65001 > nul
title JARVIS TITAN-X QUANTUM MATRIX
color 0A
echo ======================================================================
echo          [+] JARVIS MARK-VII x TITAN-X QUANTUM MATRIX [+]
echo ======================================================================
echo.
echo Navigating to project directory...
cd /d "C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot"
echo Launching Titan-X Autonomous Consensus Council...
python -m engine.orchestrator
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Bot exited with code %ERRORLEVEL%.
    pause
)
