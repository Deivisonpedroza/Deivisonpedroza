@echo off
rem Faz o robo iniciar sozinho quando este usuario entrar no Windows. Rode UMA vez.
set "ROBO=%~dp0iniciar.bat"
schtasks /Create /TN "BlingPrint" /TR "\"%ROBO%\"" /SC ONLOGON /RL LIMITED /F
echo.
echo Pronto. Ative tambem o login automatico do Windows e a opcao "ligar apos queda de energia" na BIOS.
pause
