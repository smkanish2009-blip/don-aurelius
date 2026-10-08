@echo off
title Don Aurelius - Nolan Trailer 1080x1920 60FPS Renderer
cd /d "C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot"
echo ==============================================================================
echo [DON AURELIUS] Rendering 90-Second Cinematic Christopher Nolan Trailer
echo Format: 1080x1920 @ 60.0 FPS ^| 5400 Frames ^| Stereo Nolan Master Audio
echo Target: out\don_aurelius_nolan_trailer.mp4
echo ==============================================================================
node node_modules\@remotion\cli\remotion-cli.js render src\index.ts DonAureliusNolanTrailer out\don_aurelius_nolan_trailer.mp4 --concurrency 4
if exist "out\don_aurelius_nolan_trailer.mp4" (
    echo.
    echo ==============================================================================
    echo [SUCCESS] Trailer rendered successfully to out\don_aurelius_nolan_trailer.mp4
    echo ==============================================================================
    explorer.exe /select,"C:\Users\LENOVO\.gemini\antigravity\scratch\xauusd-ai-bot\out\don_aurelius_nolan_trailer.mp4"
)
pause
