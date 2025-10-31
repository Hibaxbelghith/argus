@echo off
echo ========================================
echo   Argus - Systeme de Detection
echo ========================================
echo.
echo Demarrage du serveur Django...
echo.

cd /d "%~dp0"
call ..\env\Scripts\activate.bat
python manage.py runserver

pause
