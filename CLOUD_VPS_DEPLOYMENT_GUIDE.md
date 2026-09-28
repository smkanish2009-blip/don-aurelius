# 👑 DON AURELIUS • 24/7 CLOUD HOSTING MASTER GUIDE

---

## 🏛️ OVERVIEW: RUNNING 100% INDEPENDENT OF YOUR LAPTOP

To have your bot trade, trail stops, and send Telegram updates 24/7 while your laptop is **completely turned off and unplugged**, you now have two battle-tested avenues ready:

---

## 🚀 METHOD 1: NATIVE MT5 MQL5 VPS (FASTEST — 30 SECONDS)

Our upgraded Expert Advisor `Don_Aurelius.ex5` now has **built-in Telegram WebRequest** engine and automated 15-minute briefings compiled directly into the binary!

### Step 1: Open MetaTrader 5
1. On the left side of your MT5 screen, find the **Navigator** window (or press `Ctrl + N`).
2. Expand **Expert Advisors** ➔ find **`Don_Aurelius`**.
3. Drag **`Don_Aurelius`** onto your **XAUUSD (M15)** chart.
4. In the settings popup window:
   * Under the **Common** tab: Check **"Allow algorithmic trading"**.
   * Under the **Inputs** tab: Ensure `InpTelegramEnabled = true`, `InpTelegramToken` and `InpTelegramChatID` are filled (they are already preset!).
   * Click **OK**.

### Step 2: Register MQL5 Virtual Server
1. In the **Navigator** window, right-click on your trading account number (`10434714118`) at the very top.
2. Click **"Register a Virtual Server"**.
3. The MetaQuotes Virtual Hosting wizard will open:
   * Select a hosting plan (MetaQuotes offers a **Free 24-Hour Trial** or standard low-cost plan).
   * Click **Next**.
4. In the migration window, choose:
   * **"Migrate all: experts, charts and signals"**.
5. Click **Finish**.

> [!NOTE]
> **Done!** The MetaQuotes cloud now runs `Don_Aurelius` 24 hours a day, 365 days a year with 1 ms ping. It executes trades, trails Stop Losses into profit, and sends 15-minute briefings to your Telegram phone even when your laptop is completely powered off!

---

## ⚡ METHOD 2: DEDICATED WINDOWS CLOUD VPS (FULL AI + PYTHON + VOICE)

If you want the **entire Python 4-Agent War Room** (Hawk, Radar, Predator, Inquisitor) and **ElevenLabs Brian Voice Notes** running 24/7 in the cloud:

### Recommended Providers:
* **AWS EC2 (Amazon Web Services)**: **Free for 12 months** on the AWS Free Tier (`t2.micro` or `t3.micro` Windows Server 2022).
* **Contabo Cloud VPS**: **$5.50 / month** (6 vCPU Cores, 16 GB RAM — huge power).
* **Kamatera**: **30-Day Free Trial** Windows Cloud VM.

### 5-Minute Turnkey Setup on Any Windows Cloud VPS:
1. Log in to your Windows Cloud VPS via **Remote Desktop (RDP)** from your laptop or phone.
2. Copy the `xauusd-ai-bot` folder to the cloud VPS (or clone from Git).
3. Right-click on **`Deploy-CloudVPS.ps1`** and choose **"Run with PowerShell"**.
4. The script automatically:
   * Installs Python 3.12 64-bit unattended.
   * Installs all Python dependencies.
   * Downloads and installs MetaTrader 5.
   * Configures Windows Task Scheduler to start the bot automatically on boot.
   * Locks power settings to prevent sleep.
5. Log into your MT5 broker account once on the VPS, and launch `start_sovereign_bot.bat`.

---

## 🛡️ CURRENT LIVE ACCOUNT STATUS

* **Account Realized Balance**: **`$100,773.18 USD`** (Realized Profit: **+$773.18 USD**)
* **Account Treasury Equity**: **`$100,398.97 USD`**
* **Active Open Contracts**: 3 Short positions protected by trailing stops.
* **Local Laptop Power Plan**: Configured via `powercfg` — Lid close is set to "Do Nothing", Sleep is set to "Never".
