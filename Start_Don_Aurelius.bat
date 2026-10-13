@echo off
title Don Aurelius AI Bot - Trading Engine
echo ===================================================
echo     DON AURELIUS AI BOT - LIVE TRADING ENGINE      
echo ===================================================
echo.
echo Starting Don Aurelius Multi-Agent War Room...
echo (Close this window anytime to STOP the bot)
echo.
cd /d "C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot"
"C:\Users\LENOVO\AppData\Local\Python\pythoncore-3.14-64\python.exe" -u -m engine.orchestrator
pause
