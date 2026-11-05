@echo off
title Push InternHub to GitHub
cd /d "%~dp0"
cls
echo =====================================================================
echo                 PUSH INTERNHUB TO GITHUB REPOSITORY
echo =====================================================================
echo Target Repository: https://github.com/ragath-2006/interhub.git
echo.
echo Staging and committing changes...
git add .
git commit -m "Update student email addresses to @email.com domain"
echo.
echo Pushing files to GitHub now, please wait...
echo ---------------------------------------------------------------------
git push origin main
echo ---------------------------------------------------------------------
echo.
echo =====================================================================
echo Push complete! Check your Render Dashboard to watch it redeploy.
echo =====================================================================
pause
