@echo off
REM Author:  br435t
REM Created: 2026-10-23
REM Update this folder to a tagged GitHub release (v1.0.0, v0.9.5 Public Beta, ...). Double-click it.
REM Uses only PowerShell, which comes with Windows. Your current files are backed up to C:\Temp first.
REM
REM Keep everything after this comment on ONE line. The update replaces this file while it runs, and
REM cmd re-reads a running batch file, so the last line must be the one that ends the script.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1" %* & if "%~1"=="" pause & exit /b
