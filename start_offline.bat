@echo off
title InternHub - Offline Production Deployment
cd /d "%~dp0"
python prod_server.py
pause
