@echo off
REM Author:  br435t
REM Created: 2026-07-21
setlocal enableextensions

REM ============================================================
REM  Clear-NX-TC-Cache.bat
REM  Automates the NX / Teamcenter cache-clear procedure
REM  described in instructions.txt.
REM
REM  Steps:
REM    1. Kill NX (ugraf.exe) and Teamcenter processes.
REM    2. Kill the Zulu Java process used by NX/TC.
REM    3. Delete the contents of %LOCALAPPDATA%\Temp
REM       (files/folders in use are skipped automatically).
REM    4. Delete the Siemens, FCCCache and Teamcenter
REM       folders from the user profile (if they exist).
REM ============================================================

echo(
echo === NX / Teamcenter Cache Clear ===
echo(

REM ------------------------------------------------------------
REM Step 1: Kill NX and Teamcenter processes
REM ------------------------------------------------------------
echo [1/4] Stopping NX (ugraf.exe)...
taskkill /F /IM "ugraf.exe" >nul 2>&1 && echo   - stopped ugraf.exe || echo   - ugraf.exe not running

REM ------------------------------------------------------------
REM Step 2: Kill the Zulu Java process(es) used by NX/TC
REM   Every java.exe / javaw.exe launched from the Siemens
REM   PLM install (C:\SPLM) is terminated, so other Java
REM   apps are left alone. Multiple instances are all killed.
REM ------------------------------------------------------------
echo [2/4] Stopping NX/TC Java (Zulu) process(es)...
set "_killedjava="
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'javaw.exe' -or $_.Name -eq 'java.exe') -and $_.ExecutablePath -like 'C:\SPLM\*' } | Select-Object -ExpandProperty ProcessId"`) do (
    taskkill /F /PID %%I >nul 2>&1 && echo   - stopped Java PID %%I && set "_killedjava=1"
)
if not defined _killedjava echo   - no Zulu Java process(es) found

REM ------------------------------------------------------------
REM Step 3: Delete the contents of the Temp folder
REM   Locked / in-use files are skipped automatically because
REM   del and rd continue past files they cannot remove.
REM ------------------------------------------------------------
echo [3/4] Clearing "%LOCALAPPDATA%\Temp" contents...
if exist "%LOCALAPPDATA%\Temp\" (
    pushd "%LOCALAPPDATA%\Temp"
    del /f /s /q *.* >nul 2>&1
    for /d %%D in (*) do rd /s /q "%%D" >nul 2>&1
    popd
    echo   - done ^(items in use were left in place^)
) else (
    echo   - Temp folder not found, skipping
)

REM ------------------------------------------------------------
REM Step 4: Delete profile cache folders (if they exist)
REM ------------------------------------------------------------
echo [4/4] Removing profile cache folders...
for %%F in (Siemens FCCCache Teamcenter) do (
    if exist "%USERPROFILE%\%%F\" (
        rd /s /q "%USERPROFILE%\%%F" >nul 2>&1
        if exist "%USERPROFILE%\%%F\" (
            echo   - could not fully remove %%F ^(may be in use^)
        ) else (
            echo   - removed %%F
        )
    ) else (
        echo   - %%F not present
    )
)

echo(
echo === Cache clear complete ===
echo(
pause
endlocal
