@echo off
REM ============================================================
REM  Installs a Windows scheduled task for the CURRENT USER that
REM  runs clear_Edge-TC-cookies.ps1 every day at midnight.
REM
REM    install_schedule.bat            install / update the task
REM    install_schedule.bat remove     remove the task
REM
REM  No admin rights needed. The task runs only while this user is
REM  logged in (it clears this user's Edge profile).
REM ============================================================
setlocal
set "TASK=Clear Edge TC Cookies"
set "SCRIPT=%~dp0clear_Edge-TC-cookies.ps1"

if /i "%~1"=="remove" (
  schtasks /Delete /TN "%TASK%" /F
  goto :done
)

if not exist "%SCRIPT%" (
  echo [ERROR] Script not found: %SCRIPT%
  exit /b 1
)

schtasks /Create /TN "%TASK%" /SC DAILY /ST 00:00 /F ^
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%SCRIPT%\" -NoRestart"
if errorlevel 1 (
  echo [ERROR] Failed to create the scheduled task.
  exit /b 1
)

REM Run a missed midnight job as soon as the PC is available again
powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName '%TASK%'; $t.Settings.StartWhenAvailable = $true; Set-ScheduledTask -InputObject $t | Out-Null"

echo.
echo Installed "%TASK%": daily at 12:00 AM for user %USERNAME%.
echo Remove with: install_schedule.bat remove

:done
endlocal
