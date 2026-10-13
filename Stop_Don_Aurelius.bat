@echo off
title Stop Don Aurelius AI Bot
echo ===================================================
echo           STOPPING DON AURELIUS BOT                
echo ===================================================
echo.
powershell -Command "Get-Process python, pythonw -ErrorAction SilentlyContinue | Where-Object { $_.Path -match 'pythoncore-3.14-64' } | Stop-Process -Force"
echo Bot processes stopped.
timeout /t 3
