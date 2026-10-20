@echo off
chcp 65001 >nul
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
  echo Python nao encontrado. Instale em python.org marcando a caixa "Add Python to PATH" e rode de novo.
  pause
  exit /b 1
)
if not exist .venv python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
if not exist .env copy .env.example .env
if not exist stores.json copy stores.example.json stores.json
echo.
echo Pronto. Vao abrir 2 arquivos no Bloco de Notas: preencha, salve (Ctrl+S) e feche.
pause
notepad .env
notepad stores.json
