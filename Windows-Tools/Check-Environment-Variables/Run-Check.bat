@echo off
REM Double-click this to run Check-Environment-Variables.ps1.
REM It bypasses the PowerShell execution policy (a script downloaded in a zip is
REM often blocked otherwise, and the window would close instantly) and keeps the
REM window open at the end so the result can be read.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%~dp0' -Filter *.ps1 | Unblock-File" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check-Environment-Variables.ps1" -NoPause %*
echo.
echo ------------------------------------------------------------
echo  Finished (exit code %errorlevel%). The report file is in:
echo  %~dp0
echo ------------------------------------------------------------
pause
