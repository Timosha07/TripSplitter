@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" local_setup.py stop
pause
