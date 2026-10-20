@echo off
rem Inicia o robo. Se ele cair, reinicia sozinho apos 15 s. Deixe esta janela aberta (ou use a tarefa agendada).
cd /d "%~dp0\..\.."
:loop
.venv\Scripts\python.exe -m bling_print watch >> data\run.log 2>&1
timeout /t 15 /nobreak >nul
goto loop
