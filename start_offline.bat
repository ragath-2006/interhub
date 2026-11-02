@echo off
title InternHub - Offline Production Deployment
cd /d "%~dp0"
echo Starting InternHub Offline Production Server...
timeout /t 1 /nobreak >nul
start http://127.0.0.1:5000
python prod_server.py
pause
