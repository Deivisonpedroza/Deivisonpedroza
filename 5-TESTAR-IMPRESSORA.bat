@echo off
chcp 65001 >nul
cd /d "%~dp0"
.venv\Scripts\python -m bling_print testprint --store coruripe
echo.
pause
