@echo off
REM ============================================================
REM  Create-McMaster-Part - one-click setup
REM  Double-click this file. It creates the Python virtual
REM  environment the scraper needs, installs dependencies
REM  (works behind the corporate SSL proxy), and logs in to
REM  McMaster. Pass "nologin" to skip the McMaster login step.
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   Create-McMaster-Part  -  one-click setup
echo ============================================================
echo.

REM --- 1. Find a Python interpreter -------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo [ERROR] Python was not found on this machine.
  echo.
  echo   Install Python 3.10+ from https://www.python.org/downloads/
  echo   ^(tick "Add python.exe to PATH" during install^), then run this again.
  echo.
  pause
  exit /b 1
)
echo [1/5] Python found:
%PY% --version
echo.

REM --- 2. Create the virtual environment -------------------------------
if exist ".venv\Scripts\python.exe" (
  echo [2/5] Virtual environment .venv already exists - reusing it.
) else (
  echo [2/5] Creating virtual environment .venv ...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Could not create the virtual environment.
    pause
    exit /b 1
  )
)
set "VENV_PY=%CD%\.venv\Scripts\python.exe"
echo.

REM --- 3. Install dependencies (corporate-SSL safe) --------------------
REM  pip-system-certs makes pip trust the Windows cert store (the corporate
REM  root CA lives there), so later installs verify normally. It is
REM  bootstrapped with --trusted-host because that first install is what
REM  the SSL interception blocks.
echo [3/5] Installing dependencies ...
"%VENV_PY%" -m pip install --disable-pip-version-check --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org pip-system-certs
if errorlevel 1 (
  echo [ERROR] Could not install pip-system-certs. See messages above.
  pause
  exit /b 1
)
"%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Could not install scraper requirements. See messages above.
  pause
  exit /b 1
)
echo.

REM --- 4. Extract the NX Open MCP server -------------------------------
REM  NX_Open_MCP.zip -> MCP\ (git-ignored) and register it as the "nxopen"
REM  MCP server in .mcp.json, run with the .venv python (which has `mcp`).
echo [4/5] Setting up the NX Open MCP server ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_mcp.ps1" -Root "%CD%" -VenvPython "%VENV_PY%"
if errorlevel 1 (
  echo [ERROR] Could not set up the NX Open MCP server. See messages above.
  pause
  exit /b 1
)
echo.

REM --- 5. Log in to McMaster (opens Edge) ------------------------------
if /i "%~1"=="nologin" (
  echo [5/5] Skipping McMaster login ^(nologin^). You can run it later with:
  echo        .venv\Scripts\python.exe lib\scraper\mcmaster_scraper.py login
) else (
  echo [5/5] Opening McMaster login - sign in when the browser appears.
  echo        ^(This is optional; the tool also prompts to log in on demand.^)
  "%VENV_PY%" lib\scraper\mcmaster_scraper.py login
)
echo.

echo ============================================================
echo   Setup complete.
echo.
echo   To create a part:
echo     1. Open NX 2506 with an active Teamcenter session.
echo     2. File ^> Execute ^> NX Open...
echo     3. Select:  %CD%\NX-Scripts\Create-McMaster-Part\CREATE_MCMASTER_PART.py
echo.
echo   NX Open MCP: restart Claude Code in this folder so the "nxopen"
echo   server ^(search_nxopen tool^) loads.
echo ============================================================
echo.
pause
