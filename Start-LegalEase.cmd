@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run Install-LegalEase.cmd first. See START_HERE.md for instructions.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" run.py
if errorlevel 1 pause
