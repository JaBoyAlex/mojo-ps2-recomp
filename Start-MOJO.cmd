@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0builder\bootstrap.ps1" %*
set "result=%errorlevel%"
if not "%result%"=="0" pause
exit /b %result%
