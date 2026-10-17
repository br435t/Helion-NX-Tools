@echo off
rem Shows who is using each NX license feature and saves the report to <repo>\output.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0CheckLicenses.ps1"
pause
