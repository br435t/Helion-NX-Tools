<#
.SYNOPSIS
  Diagnoses the NX startup warning:
    "Unable to append module directory path in PYTHONPATH. Please make sure that
     UGII_PYTHONPATH environment variable is correctly defined."

.DESCRIPTION
  NX appends every folder in UGII_PYTHONPATH to Python's search path at startup.
  The warning means one of those folders is missing or the value is malformed.
  UGII_PYTHONPATH can come from TWO places, and this script reports on both:

    Part 1 - Windows environment variables (User / Machine / current session).
    Part 2 - NX's own definition in <NX install>\UGII\ugii_env_ug.dat, with every
             ${VAR} expanded and each resulting folder checked. This is where a
             missing or incomplete NX install shows up. Also reports launcher
             overrides (UGII_ENV_FILE / UGII_CUSTOM_DIRECTORY_FILE).

  By default nothing is changed. Send the report file (saved next to this script) to
  whoever is supporting you.

  -Fix rewrites only the USER-level Windows variable (Part 1) without bad
  entries, after saving a backup next to this script. It never edits NX files or the
  Machine-level variable.

.PARAMETER NoPause
  By default the script waits for Enter before closing when it was started from
  Explorer (double-click / right-click > Run with PowerShell), so the window
  doesn't vanish. Pass -NoPause to skip that.

.PARAMETER NxDir
  NX install folder (e.g. C:\SPLM\NX\NX2506). Auto-detected if omitted.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\Check-UGII-PythonPath.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\Check-UGII-PythonPath.ps1 -NxDir C:\SPLM\NX\NX2506
#>
param(
    [switch]$Fix,
    [string]$NxDir,
    [switch]$NoPause   # don't wait for Enter at the end (Run-Check.bat does its own pause)
)

$ErrorActionPreference = 'Stop'
$VarName = 'UGII_PYTHONPATH'
# Output (report + any -Fix backup) goes next to this script.
$OutDir  = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$Report  = Join-Path $OutDir "UGII_PYTHONPATH-report-$Stamp.txt"
$Lines   = New-Object System.Collections.Generic.List[string]
$Problems = New-Object System.Collections.Generic.List[string]

# True when this process was started from Explorer (double-click), i.e. the
# console would close the moment the script ends.
function Test-StartedFromExplorer {
    try {
        $parentId = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
        return ((Get-Process -Id $parentId -ErrorAction Stop).ProcessName -eq 'explorer')
    } catch { return $false }
}

function Wait-BeforeClose {
    if ($NoPause) { return }
    if (Test-StartedFromExplorer) {
        Write-Host ''
        Write-Host 'Press Enter to close this window...'
        try { [void][Console]::ReadLine() } catch { }
    }
}

# On an unexpected error: save what we have, then show a window with an Exit
# button (so a double-clicked/launcher window doesn't just vanish) and quit.
function Show-ErrorAndExit($errorRecord) {
    $message = "The check failed with an unexpected error:`r`n`r`n" +
               "$($errorRecord.Exception.Message)`r`n`r`n" +
               "At: $($errorRecord.InvocationInfo.PositionMessage)"
    Write-Host ''
    Write-Host $message -ForegroundColor Red
    try {
        $Lines.Add('')
        $Lines.Add('UNEXPECTED ERROR')
        $Lines.Add($message)
        Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
        Write-Host "Partial report saved to: $Report"
    } catch { }
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $form = New-Object System.Windows.Forms.Form
        $form.Text = 'Check-UGII-PythonPath - Error'
        $form.Size = New-Object System.Drawing.Size(560, 340)
        $form.StartPosition = 'CenterScreen'
        $form.TopMost = $true
        $box = New-Object System.Windows.Forms.TextBox
        $box.Multiline = $true
        $box.ReadOnly = $true
        $box.ScrollBars = 'Vertical'
        $box.Text = $message + "`r`n`r`nA partial report was saved next to the script:`r`n$Report"
        $box.Location = New-Object System.Drawing.Point(12, 12)
        $box.Size = New-Object System.Drawing.Size(520, 240)
        $exit = New-Object System.Windows.Forms.Button
        $exit.Text = 'Exit'
        $exit.Size = New-Object System.Drawing.Size(90, 30)
        $exit.Location = New-Object System.Drawing.Point(442, 262)
        $exit.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $form.AcceptButton = $exit
        $form.CancelButton = $exit
        $form.Controls.AddRange(@($box, $exit))
        [void]$form.ShowDialog()
    } catch {
        # No GUI available: fall back to the console.
        Write-Host 'Press Enter to exit...'
        try { [void][Console]::ReadLine() } catch { }
    }
    exit 1
}

trap { Show-ErrorAndExit $_ }

function Say([string]$text) {
    Write-Host $text
    $Lines.Add($text)
}

# Verdict for one folder entry: $null if fine, else a short reason.
function Test-Entry([string]$entry) {
    if ($entry.Trim() -eq '') { return 'empty entry (stray or trailing ";")' }
    $clean = $entry.Trim()
    if ($clean -match '"') { return 'contains quote characters' }
    if ($clean -match '%[^%]+%') {
        $clean = [Environment]::ExpandEnvironmentVariables($clean)
        if ($clean -match '%[^%]+%') { return 'refers to an undefined environment variable' }
    }
    if (Test-Path -LiteralPath $clean -PathType Container) { return $null }
    if (Test-Path -LiteralPath $clean -PathType Leaf) {
        # NX also accepts .zip files on the Python path (e.g. Python312.zip).
        if ($clean -match '\.(zip|egg)$') { return $null }
        return 'is a file, not a folder'
    }
    return 'does not exist'
}

function Get-Entries([string]$value) {
    $out = @()
    if ([string]::IsNullOrEmpty($value)) { return $out }
    $i = 0
    foreach ($raw in $value.Split(';')) {
        $i++
        $out += [pscustomobject]@{ Index = $i; Entry = $raw; Problem = (Test-Entry $raw) }
    }
    return $out
}

function Show-Entries($entries, [string]$label) {
    $bad = 0
    foreach ($e in $entries) {
        if ($e.Problem) {
            $bad++
            Say ("  {0,2}. PROBLEM  {1}  <-- {2}" -f $e.Index, $e.Entry, $e.Problem)
            $Problems.Add("$label entry $($e.Index): '$($e.Entry)' $($e.Problem)")
        } else {
            Say ("  {0,2}. ok       {1}" -f $e.Index, $e.Entry)
        }
    }
    return $bad
}

Say "UGII_PYTHONPATH check - $(Get-Date)"
Say "Computer: $env:COMPUTERNAME   User: $env:USERNAME"

# ============================================================================
# PART 1 - Windows environment variables
# ============================================================================
Say ''
Say ('=' * 70)
Say 'PART 1: Windows environment variable UGII_PYTHONPATH'
Say ('=' * 70)

$userBad = 0
foreach ($scopeName in 'User', 'Machine', 'Process') {
    $value = [Environment]::GetEnvironmentVariable($VarName, $scopeName)
    Say ''
    Say "[$scopeName]"
    if ([string]::IsNullOrEmpty($value)) { Say '  (not set)'; continue }
    Say "  Value  : $value"
    Say "  Length : $($value.Length) characters"
    $bad = Show-Entries (Get-Entries $value) "Windows/$scopeName"
    if ($scopeName -eq 'User') { $userBad = $bad }
}

# ============================================================================
# PART 2 - NX's own definition (ugii_env_ug.dat)
# ============================================================================
Say ''
Say ('=' * 70)
Say "PART 2: NX's own definition (ugii_env_ug.dat)"
Say ('=' * 70)

# --- locate the NX install ---------------------------------------------------
if (-not $NxDir) { $NxDir = $env:UGII_BASE_DIR }
if (-not $NxDir) {
    $candidates = @(Get-ChildItem 'C:\SPLM\NX' -Directory -ErrorAction SilentlyContinue |
                    Sort-Object Name -Descending)
    if ($candidates.Count -gt 0) { $NxDir = $candidates[0].FullName }
}
Say ''
if (-not $NxDir -or -not (Test-Path -LiteralPath $NxDir -PathType Container)) {
    Say "NX install folder not found (looked at UGII_BASE_DIR and C:\SPLM\NX\*)."
    Say 'Re-run with -NxDir <install folder>, e.g. -NxDir C:\SPLM\NX\NX2506'
    $Problems.Add('NX install folder could not be found')
} else {
    $NxDir = $NxDir.TrimEnd('\')
    Say "NX install folder : $NxDir"
    $envDat = Join-Path $NxDir 'UGII\ugii_env_ug.dat'
    if (-not (Test-Path -LiteralPath $envDat)) {
        Say "MISSING: $envDat"
        $Problems.Add("ugii_env_ug.dat not found at $envDat")
    } else {
        Say "Reading           : $envDat"

        # Parse KEY=VALUE lines (later definitions win, as in NX).
        $vars = @{}
        foreach ($line in [System.IO.File]::ReadAllLines($envDat)) {
            $t = $line.Trim()
            if ($t -eq '' -or $t.StartsWith('#')) { continue }
            $eq = $t.IndexOf('=')
            if ($eq -lt 1) { continue }
            $vars[$t.Substring(0, $eq).Trim().ToUpperInvariant()] = $t.Substring($eq + 1).Trim()
        }
        # Variables NX sets before reading the file.
        if (-not $vars.ContainsKey('UGII_BASE_DIR')) { $vars['UGII_BASE_DIR'] = $NxDir }
        $vars['UGII_BASE_DIR'] = $NxDir

        function Expand-NxVars([string]$text, [int]$depth = 0) {
            if ($depth -gt 12) { return $text }
            $result = [regex]::Replace($text, '\$\{([^}]+)\}|\$([A-Za-z0-9_]+)', {
                param($m)
                $name = if ($m.Groups[1].Success) { $m.Groups[1].Value } else { $m.Groups[2].Value }
                $key = $name.ToUpperInvariant()
                if ($vars.ContainsKey($key)) { return $vars[$key] }
                $envValue = [Environment]::GetEnvironmentVariable($name, 'Process')
                if ($envValue) { return $envValue }
                return $m.Value   # leave undefined variables visible
            })
            if ($result -ne $text -and $result -match '\$') { return Expand-NxVars $result ($depth + 1) }
            return $result
        }

        if (-not $vars.ContainsKey($VarName)) {
            Say "$VarName is not defined in this file."
        } else {
            Say ''
            Say "Definition        : $($vars[$VarName])"
            $expanded = Expand-NxVars $vars[$VarName]
            Say "Expanded to       : $expanded"
            Say ''
            $bad = Show-Entries (Get-Entries $expanded) 'NX ugii_env_ug.dat'
            if ($bad -gt 0) {
                Say ''
                Say '  The PROBLEM folders above are missing from this NX install, or a'
                Say '  ${VAR} could not be resolved. That is the likely cause of the warning.'
            }
        }
    }
}

# --- launcher overrides ------------------------------------------------------
Say ''
Say 'Launcher overrides (set by the NX launcher/shortcut, so only visible if this'
Say 'script runs from the same launcher):'
foreach ($name in 'UGII_ENV_FILE', 'UGII_CUSTOM_DIRECTORY_FILE', 'UGII_BASE_DIR',
                  'UGII_PYTHON_HOME', 'UGII_ROOT_DIR', 'PYTHONHOME', 'PYTHONPATH') {
    $v = [Environment]::GetEnvironmentVariable($name, 'Process')
    if (-not $v) { Say "  $name = (not set)"; continue }
    Say "  $name = $v"
    if ($name -in 'UGII_ENV_FILE', 'UGII_CUSTOM_DIRECTORY_FILE') {
        if (-not (Test-Path -LiteralPath $v -PathType Leaf)) {
            Say "      PROBLEM: that file does not exist"
            $Problems.Add("$name points to a missing file: $v")
        } elseif ($name -eq 'UGII_ENV_FILE') {
            $hits = @(Select-String -LiteralPath $v -Pattern 'UGII_PYTHON' -ErrorAction SilentlyContinue |
                      Where-Object { $_.Line.Trim() -notmatch '^#' })
            foreach ($h in $hits) { Say "      overrides: $($h.Line.Trim())" }
        } else {
            foreach ($l in [System.IO.File]::ReadAllLines($v)) {
                $t = $l.Trim()
                if ($t -eq '' -or $t.StartsWith('#')) { continue }
                if ($t -match '^[A-Za-z]:\\|^\\\\') {
                    if (-not (Test-Path -LiteralPath $t -PathType Container)) {
                        Say "      PROBLEM: custom directory does not exist: $t"
                        $Problems.Add("custom_dirs entry missing: $t")
                    }
                }
            }
        }
    }
}

# ============================================================================
# SUMMARY
# ============================================================================
Say ''
Say ('=' * 70)
if ($Problems.Count -eq 0) {
    Say 'RESULT: no problems found in either place.'
    Say 'If NX still shows the warning, send this report to your support contact.'
} else {
    Say "RESULT: $($Problems.Count) problem(s) found:"
    foreach ($p in $Problems) { Say "  - $p" }
    if ($Problems | Where-Object { $_ -like 'Windows/Machine*' }) {
        Say 'The MACHINE-level variable needs an administrator to change.'
    }
}

if ($Fix) {
    Say ''
    $userValue = [Environment]::GetEnvironmentVariable($VarName, 'User')
    if ($userBad -gt 0) {
        $backup = Join-Path $OutDir "UGII_PYTHONPATH-user-backup-$Stamp.txt"
        Set-Content -LiteralPath $backup -Value $userValue -Encoding UTF8
        Say "Backed up the original USER value to: $backup"
        $good = @(Get-Entries $userValue | Where-Object { -not $_.Problem } |
                  ForEach-Object { $_.Entry.Trim() })
        if ($good.Count -gt 0) {
            [Environment]::SetEnvironmentVariable($VarName, ($good -join ';'), 'User')
            Say "FIXED: USER $VarName is now: $($good -join ';')"
        } else {
            [Environment]::SetEnvironmentVariable($VarName, $null, 'User')
            Say "FIXED: USER $VarName had no valid folders and was removed."
        }
        Say 'Close and reopen NX (and any terminals) for the change to take effect.'
    } else {
        Say '-Fix: the USER-level Windows variable has no bad entries; nothing changed.'
    }
}

try {
    Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
    Write-Host ''
    Write-Host "Report saved to: $Report"
} catch {
    Write-Host "(Could not save the report file: $($_.Exception.Message))"
}

Wait-BeforeClose
