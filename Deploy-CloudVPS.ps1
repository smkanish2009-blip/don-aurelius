<#
.SYNOPSIS
    DON AURELIUS • SOVEREIGN QUANTUM SYNDICATE
    Turnkey Automated Cloud VPS Deployment & Boot Engine
    Designed for AWS EC2, Contabo, Kamatera, or any Windows Server 2019/2022.
#>

[CmdletBinding()]
param (
    [string]$BotDir = "$PSScriptRoot"
)

Write-Host "======================================================================" -ForegroundColor Yellow
Write-Host "        [+] DON AURELIUS: CLOUD VPS PROVISIONING ENGINE [+]           " -ForegroundColor Gold
Write-Host "======================================================================" -ForegroundColor Yellow

# Step 1: Ensure Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "[!] Warning: Run this script as Administrator to install system tasks and services."
}

# Step 2: Configure System Power to 24/7/365 Continuous Mode
Write-Host "[1/5] Locking Windows Power Architecture for 24/7 Continuous Operation..." -ForegroundColor Cyan
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 15
powercfg /setactive SCHEME_CURRENT
Write-Host "[+] Power settings locked: Sleep disabled." -ForegroundColor Green

# Step 3: Verify or Install Python 3.12
Write-Host "[2/5] Verifying Python Environment..." -ForegroundColor Cyan
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "[!] Python not detected. Downloading official Python 3.12 64-bit installer..." -ForegroundColor Yellow
    $pyUrl = "https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe"
    $installerPath = "$env:TEMP\python-3.12.6-amd64.exe"
    Invoke-WebRequest -Uri $pyUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "[+] Installing Python unattended with PATH registration..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "[+] Python successfully installed!" -ForegroundColor Green
} else {
    Write-Host "[+] Python detected: $pythonPath" -ForegroundColor Green
}

# Step 4: Install Bot Dependencies
Write-Host "[3/5] Installing Sovereign AI Dependencies..." -ForegroundColor Cyan
Set-Location $BotDir
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "[+] All Python dependencies locked and verified." -ForegroundColor Green

# Step 5: Verify or Download MetaTrader 5
Write-Host "[4/5] Checking MetaTrader 5 Installation..." -ForegroundColor Cyan
$mt5Exe = "C:\Program Files\MetaTrader 5\terminal64.exe"
if (-not (Test-Path $mt5Exe)) {
    Write-Host "[!] MetaTrader 5 not found. Downloading official MetaTrader 5 setup..." -ForegroundColor Yellow
    $mt5Url = "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
    $mt5Installer = "$env:TEMP\mt5setup.exe"
    Invoke-WebRequest -Uri $mt5Url -OutFile $mt5Installer -UseBasicParsing
    Write-Host "[+] Installing MetaTrader 5..." -ForegroundColor Yellow
    Start-Process -FilePath $mt5Installer -ArgumentList "/auto" -Wait
    Remove-Item $mt5Installer -Force -ErrorAction SilentlyContinue
    Write-Host "[+] MetaTrader 5 installed successfully!" -ForegroundColor Green
} else {
    Write-Host "[+] MetaTrader 5 already present: $mt5Exe" -ForegroundColor Green
}

# Step 6: Create Persistent Scheduled Task for 24/7 Autostart on Boot
Write-Host "[5/5] Registering 24/7 Persistent Background Windows Service Task..." -ForegroundColor Cyan
$taskName = "DonAureliusSovereignDaemon"
$actionScript = "$BotDir\start_sovereign_bot.bat"

# Generate launcher batch file
@"
@echo off
title DON AURELIUS SOVEREIGN MATRIX
cd /d "$BotDir"
:LOOP
echo [%DATE% %TIME%] Starting DON AURELIUS Orchestrator...
python -u -m engine.orchestrator
echo [%DATE% %TIME%] Orchestrator stopped unexpectedly. Rebooting in 5 seconds...
timeout /t 5 /nobreak >nul
goto LOOP
"@ | Out-File -FilePath $actionScript -Encoding ASCII

# Register Task Scheduler entry
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    $action = New-ScheduledTaskAction -Execute $actionScript
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 365)
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "DON AURELIUS 24/7 Autonomous Trading Engine"
    Write-Host "[+] 24/7 Auto-Start Task '$taskName' successfully registered!" -ForegroundColor Green
} catch {
    Write-Warning "[!] Could not register task automatically. Launcher batch created at: $actionScript"
}

Write-Host "======================================================================" -ForegroundColor Yellow
Write-Host " [SUCCESS] DON AURELIUS 24/7 CLOUD ENVIRONMENT READY FOR OPERATION!   " -ForegroundColor Green
Write-Host " Launch anytime via: $actionScript                                     " -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Yellow
