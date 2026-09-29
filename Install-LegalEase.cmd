@echo off
setlocal
cd /d "%~dp0"
echo LegalEase - first-time installation
echo Internet access is required to download Python packages.
echo.
if exist ".venv\Scripts\python.exe" goto install

py -3.13 -c "import sys; sys.exit(sys.version_info[:2] != (3, 13))" >nul 2>&1
if not errorlevel 1 goto python313
py -3.12 -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if not errorlevel 1 goto python312
python -c "import sys; sys.exit(sys.version_info[:2] not in ((3, 12), (3, 13)))" >nul 2>&1
if not errorlevel 1 goto pythonpath
echo Python 3.12 or 3.13 was not found.
echo Install Python from https://www.python.org/downloads/
echo Enable Add python.exe to PATH, then run this file again.
pause
exit /b 1

:python313
py -3.13 -m venv .venv
if errorlevel 1 goto failed
goto install

:python312
py -3.12 -m venv .venv
if errorlevel 1 goto failed
goto install

:pythonpath
python -m venv .venv
if errorlevel 1 goto failed

:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
if exist ".env" goto ready
copy /y ".env.example" ".env" >nul
if errorlevel 1 goto failed

:ready
echo.
echo Installation complete.
echo Open .env in VS Code to set AI_PROVIDER=gemini and your own GEMINI_API_KEY.
echo See START_HERE.md for the exact settings.
echo Then double-click Start-LegalEase.cmd and open http://127.0.0.1:8501
pause
exit /b 0

:failed
echo.
echo Installation failed. Read the error above, check your internet connection,
echo and confirm Python 3.12 or 3.13 is installed. Then run this file again.
pause
exit /b 1
