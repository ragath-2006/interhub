@echo off
title InternHub - Live Worldwide Deployment
echo ========================================================
echo        INTERNHUB - LIVE WORLDWIDE DEPLOYMENT
echo ========================================================
cd /d "%~dp0"
echo [1/2] Starting Production Backend Server...
start "InternHub Server" cmd /c "python prod_server.py"
timeout /t 3 /nobreak >nul
echo [2/2] Launching Cloudflare Public Tunnel...
echo.
echo Your public HTTPS link will appear below:
echo ========================================================
.\cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
