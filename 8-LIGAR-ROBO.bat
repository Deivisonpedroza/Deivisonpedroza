@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Robo ligado. NAO feche esta janela (minimize). Alertas chegam no Telegram.
call deploy\windows\iniciar.bat
