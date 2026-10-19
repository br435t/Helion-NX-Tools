<#
.SYNOPSIS
  Tests the Windows USER and SYSTEM (Machine) environment variables and writes a
  report. Read-only apart from a short create/read/delete test of a temporary
  variable.

.DESCRIPTION
  Reads both scopes straight from the registry (so unexpanded %VAR% references are
  visible) and checks:

    1. Every variable      : empty value, stray quotes or leading/trailing spaces,
                             %VAR% references to variables that don't exist.
    2. Path lists          : PATH, PSModulePath, UGII_PYTHONPATH, ... - each folder
                             must exist; empty entries, quoted entries and
                             duplicates are noted.
    3. Path-valued vars    : a variable whose whole value is a file/folder path
                             (e.g. UGII_BASE_DIR) must point at something that exists.
    4. User vs System      : variables set in both scopes with different values
                             (the User value wins, except for PATH which is merged).
    5. This session        : the running session's value differs from what is
                             stored (a change that needs a new sign-in/restart).
    7. NX baseline         : compares FMS_HOME, JAVA_HOME, JRE_HOME and JRE64_HOME
                             (what NX uses) with the known-good values in
                             nx-baseline.json: set, right scope, same value, and the
                             folder really contains what NX needs.
    6. Write test          : can a temporary variable be created, read back and
                             deleted? User scope always; System scope only as admin.

  PROBLEM lines are counted in the RESULT summary. NOTE lines (duplicate PATH
  entries, User/System differences, session differences) are informational.
  The report is saved next to this script.

.PARAMETER NoPause
  Don't wait for Enter at the end when started from Explorer.

.PARAMETER BaselineFile
  Known-good baseline (JSON). Defaults to nx-baseline.json next to this script;
  check 7 is skipped if the file doesn't exist.

.PARAMETER SkipWriteTest
  Skip check 6 (the temporary-variable create/read/delete test).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\Check-Environment-Variables.ps1
#>
# Author:  br435t
# Created: 2026-10-15
param(
    [switch]$NoPause,
    [switch]$SkipWriteTest,
    [string]$BaselineFile
)

$ErrorActionPreference = 'Stop'
$OutDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$Report = Join-Path $OutDir "Environment-report-$Stamp.txt"
$Lines  = New-Object System.Collections.Generic.List[string]
$Problems = New-Object System.Collections.Generic.List[string]

function Say([string]$text) { Write-Host $text; $Lines.Add($text) }
function Problem([string]$scope, [string]$text) {
    Say "  PROBLEM  [$scope] $text"
    $Problems.Add("[$scope] $text")
}
function Note([string]$text) { Say "  NOTE     $text" }
function Header([string]$title) {
    Say ''; Say ('=' * 70); Say $title; Say ('=' * 70)
}

function Test-StartedFromExplorer {
    try {
        $parentId = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
        return ((Get-Process -Id $parentId -ErrorAction Stop).ProcessName -eq 'explorer')
    } catch { return $false }
}
function Wait-BeforeClose {
    if ($NoPause) { return }
    if (Test-StartedFromExplorer) {
        Write-Host ''; Write-Host 'Press Enter to close this window...'
        try { [void][Console]::ReadLine() } catch { }
    }
}

# On an unexpected error: save a partial report, show a window with an Exit button.
function Show-ErrorAndExit($errorRecord) {
    $message = "The check failed with an unexpected error:`r`n`r`n" +
               "$($errorRecord.Exception.Message)`r`n`r`n" +
               "At: $($errorRecord.InvocationInfo.PositionMessage)"
    Write-Host ''; Write-Host $message -ForegroundColor Red
    try {
        $Lines.Add(''); $Lines.Add('UNEXPECTED ERROR'); $Lines.Add($message)
        Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
        Write-Host "Partial report saved to: $Report"
    } catch { }
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $form = New-Object System.Windows.Forms.Form
        $form.Text = 'Check-Environment-Variables - Error'
        $form.Size = New-Object System.Drawing.Size(560, 340)
        $form.StartPosition = 'CenterScreen'
        $form.TopMost = $true
        $box = New-Object System.Windows.Forms.TextBox
        $box.Multiline = $true; $box.ReadOnly = $true; $box.ScrollBars = 'Vertical'
        $box.Text = $message + "`r`n`r`nA partial report was saved next to the script:`r`n$Report"
        $box.Location = New-Object System.Drawing.Point(12, 12)
        $box.Size = New-Object System.Drawing.Size(520, 240)
        $exit = New-Object System.Windows.Forms.Button
        $exit.Text = 'Exit'
        $exit.Size = New-Object System.Drawing.Size(90, 30)
        $exit.Location = New-Object System.Drawing.Point(442, 262)
        $exit.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $form.AcceptButton = $exit; $form.CancelButton = $exit
        $form.Controls.AddRange(@($box, $exit))
        [void]$form.ShowDialog()
    } catch {
        Write-Host 'Press Enter to exit...'
        try { [void][Console]::ReadLine() } catch { }
    }
    exit 1
}
trap { Show-ErrorAndExit $_ }

# ---------------------------------------------------------------------------
# Registry readers (raw = unexpanded, so %VAR% references are visible)
# ---------------------------------------------------------------------------
function Get-Vars([string]$scope) {
    if ($scope -eq 'User') {
        $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment')
    } else {
        $key = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey(
            'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')
    }
    $vars = [ordered]@{}
    if ($null -eq $key) { return $vars }
    foreach ($name in ($key.GetValueNames() | Sort-Object)) {
        if ($name -eq '') { continue }
        $raw = $key.GetValue($name, $null, 'DoNotExpandEnvironmentNames')
        $vars[$name] = [pscustomobject]@{
            Name     = $name
            Raw      = [string]$raw
            Kind     = [string]$key.GetValueKind($name)
            Expanded = [Environment]::ExpandEnvironmentVariables([string]$raw)
        }
    }
    $key.Close()
    return $vars
}

function Test-LooksLikePath([string]$value) { return $value -match '^\s*"?[A-Za-z]:\\' -or $value -match '^\s*"?\\\\' }

function Test-PathListVar($var) {
    if ($var.Name -in 'PATH', 'PSModulePath', 'PYTHONPATH', 'UGII_PYTHONPATH', 'CLASSPATH', 'INCLUDE', 'LIB') { return $true }
    if ($var.Raw -notmatch ';') { return $false }
    $drivePaths = @($var.Raw.Split(';') | Where-Object { $_ -match '^\s*"?([A-Za-z]:\\|%)' })
    return ($drivePaths.Count -ge 2)
}

# 'dir' | 'file' | 'missing' | 'unknown' (e.g. access denied) - never throws.
function Get-PathState([string]$p) {
    try {
        if (Test-Path -LiteralPath $p -PathType Container) { return 'dir' }
        if (Test-Path -LiteralPath $p -PathType Leaf) { return 'file' }
        return 'missing'
    } catch { return 'unknown' }
}

function Normalize-Dir([string]$p) { return $p.Trim().Trim('"').TrimEnd('\').ToLowerInvariant() }

$userVars = Get-Vars 'User'
$machVars = Get-Vars 'Machine'
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Say "Environment variable check - $(Get-Date)"
Say "Computer: $env:COMPUTERNAME   User: $env:USERNAME   Admin: $isAdmin"
Say "User variables: $($userVars.Count)   System variables: $($machVars.Count)"

# ---------------------------------------------------------------------------
# Checks 1-3 per scope
# ---------------------------------------------------------------------------
foreach ($scopeName in 'User', 'System') {
    $vars = if ($scopeName -eq 'User') { $userVars } else { $machVars }
    Header "$($scopeName.ToUpper()) VARIABLES  ($($vars.Count))"
    foreach ($v in $vars.Values) {
        $shown = $v.Raw
        if ($shown.Length -gt 160) { $shown = $shown.Substring(0, 160) + " ... ($($v.Raw.Length) chars)" }
        Say ''
        Say "$($v.Name)  [$($v.Kind)]"
        Say "  $shown"

        # 1. every variable
        if ([string]::IsNullOrWhiteSpace($v.Raw)) { Problem $scopeName "$($v.Name) is empty" ; continue }
        if ($v.Raw -ne $v.Raw.Trim()) { Problem $scopeName "$($v.Name) has leading/trailing spaces" }
        if ($v.Expanded -match '%[^%]+%') {
            Problem $scopeName "$($v.Name) refers to an undefined variable: $(([regex]::Matches($v.Expanded,'%[^%]+%') | ForEach-Object { $_.Value }) -join ', ')"
        }
        if ($v.Raw -match '%' -and $v.Kind -eq 'String') {
            Note "$($v.Name) contains %VAR% text but is stored as plain text (REG_SZ), so Windows will NOT expand it in some programs."
        }

        # 2. path lists
        if (Test-PathListVar $v) {
            $seen = @{}
            $i = 0
            foreach ($entry in $v.Raw.Split(';')) {
                $i++
                if ($entry.Trim() -eq '') {
                    if ($i -lt $v.Raw.Split(';').Count) { Problem $scopeName "$($v.Name) entry $i is empty (stray ';')" }
                    continue
                }
                if ($entry -match '"') { Problem $scopeName "$($v.Name) entry $i contains quotes: $entry" }
                $expanded = [Environment]::ExpandEnvironmentVariables($entry.Trim().Trim('"'))
                if ($expanded -match '%[^%]+%') { Problem $scopeName "$($v.Name) entry $i has an undefined variable: $entry"; continue }
                switch (Get-PathState $expanded) {
                    'missing' { Problem $scopeName "$($v.Name) entry $i does not exist: $expanded" }
                    'file'    {
                        if ($expanded -notmatch '\.(zip|egg)$') {
                            Problem $scopeName "$($v.Name) entry $i is a file, not a folder: $expanded"
                        }
                    }
                    'unknown' { Note "$($v.Name) entry $i could not be checked (access denied): $expanded" }
                }
                $key = Normalize-Dir $expanded
                if ($seen.ContainsKey($key)) { Note "$($v.Name) [$scopeName] entry $i duplicates entry $($seen[$key]) (harmless): $expanded" }
                else { $seen[$key] = $i }
            }
        }
        # 3. whole value is a path
        elseif (Test-LooksLikePath $v.Raw -and $v.Raw -notmatch ';' -and $v.Expanded -notmatch ' [-/]\w') {
            $p = $v.Expanded.Trim().Trim('"')
            switch (Get-PathState $p) {
                'missing' { Problem $scopeName "$($v.Name) points at a path that does not exist: $p" }
                'unknown' { Note "$($v.Name) points at a path that could not be checked (access denied): $p" }
            }
        }
    }
}

# ---------------------------------------------------------------------------
# 4. User vs System
# ---------------------------------------------------------------------------
Header 'USER vs SYSTEM'
$both = @($userVars.Keys | Where-Object { $machVars.Contains($_) })
$shownAny = $false
foreach ($name in $both) {
    if ($name -in 'PATH', 'PSModulePath') { continue }
    if ($userVars[$name].Expanded -ne $machVars[$name].Expanded) {
        $shownAny = $true
        Note "$name is set in both with DIFFERENT values; the User value wins here."
        Say "           User  : $($userVars[$name].Raw)"
        Say "           System: $($machVars[$name].Raw)"
    }
}
if (-not $shownAny) { Say '  No variable is set to conflicting values in both scopes.' }
if ($both -contains 'PATH') {
    $u = @($userVars['PATH'].Expanded.Split(';') | Where-Object { $_.Trim() } | ForEach-Object { Normalize-Dir $_ })
    $m = @($machVars['PATH'].Expanded.Split(';') | Where-Object { $_.Trim() } | ForEach-Object { Normalize-Dir $_ })
    $dups = @($u | Where-Object { $m -contains $_ } | Select-Object -Unique)
    foreach ($d in $dups) { Note "PATH folder is in both the User and System PATH: $d" }
}

# ---------------------------------------------------------------------------
# 5. This session vs stored values
# ---------------------------------------------------------------------------
Header 'THIS SESSION vs STORED VALUES'
$sessionDiffs = 0
foreach ($name in (@($userVars.Keys) + @($machVars.Keys) | Select-Object -Unique)) {
    if ($name -in 'PATH', 'PSModulePath', 'USERNAME', 'USERDOMAIN') { continue }
    $expected = if ($userVars.Contains($name)) { $userVars[$name].Expanded } else { $machVars[$name].Expanded }
    $actual = [Environment]::GetEnvironmentVariable($name, 'Process')
    if ($actual -ne $expected) {
        $sessionDiffs++
        Note "$name differs in this session. Stored: '$expected'  Session: '$actual'"
    }
}
if ($sessionDiffs -eq 0) { Say '  This session matches the stored values.' }
else { Say '  (A changed variable only reaches programs started after a new sign-in or restart.)' }

# ---------------------------------------------------------------------------
# 6. Write test
# ---------------------------------------------------------------------------
Header 'WRITE TEST (temporary variable: create, read back, delete)'
if ($SkipWriteTest) {
    Say '  Skipped (-SkipWriteTest).'
} else {
    foreach ($scope in 'User', 'Machine') {
        $label = if ($scope -eq 'Machine') { 'System' } else { 'User' }
        if ($scope -eq 'Machine' -and -not $isAdmin) {
            Say "  [$label] skipped - needs an administrator (not an error)."
            continue
        }
        $name  = 'HELION_ENVTEST_' + ([guid]::NewGuid().ToString('N').Substring(0, 8))
        $value = 'ok-' + $Stamp
        try {
            [Environment]::SetEnvironmentVariable($name, $value, $scope)
            $back = [Environment]::GetEnvironmentVariable($name, $scope)
            if ($back -eq $value) { Say "  [$label] create + read back: ok" }
            else { Problem $label "wrote $name but read back '$back'" }
        } catch {
            Problem $label "could not create a variable: $($_.Exception.Message)"
        } finally {
            try {
                [Environment]::SetEnvironmentVariable($name, $null, $scope)
                if ($null -eq [Environment]::GetEnvironmentVariable($name, $scope)) { Say "  [$label] delete: ok" }
                else { Problem $label "could not delete the temporary variable $name (remove it by hand)" }
            } catch {
                Problem $label "could not delete the temporary variable $name : $($_.Exception.Message)"
            }
        }
    }
}

# ---------------------------------------------------------------------------
# 7. NX baseline (known-good values)
# ---------------------------------------------------------------------------
Header 'NX BASELINE (FMS_HOME, JAVA_HOME, JRE_HOME, JRE64_HOME)'
$BaselineResults = New-Object System.Collections.Generic.List[object]
$BaselineChecked = $false
$ProblemsBeforeBaseline = $Problems.Count

# Checks one baseline entry; returns @{ Name; Scope; Expected; Found; Reasons; Fix }.
function Test-BaselineVar($b) {
    $scopeLabel = if ($b.scope -eq 'Machine') { 'System' } else { 'User' }
    $sameScope  = if ($b.scope -eq 'Machine') { $machVars } else { $userVars }
    $otherScope = if ($b.scope -eq 'Machine') { $userVars } else { $machVars }
    $otherLabel = if ($b.scope -eq 'Machine') { 'User' } else { 'System' }
    $want = Normalize-Dir ([string]$b.expected)
    $reasons = New-Object System.Collections.Generic.List[string]
    $fix = "Set the $scopeLabel environment variable $($b.name) to '$($b.expected)'" +
           $(if ($scopeLabel -eq 'System') { ' (needs an administrator).' } else { '.' })

    $result = @{ Name = $b.name; Scope = $scopeLabel; Expected = [string]$b.expected
                 Found = '(not set)'; Reasons = $reasons; Fix = $fix }

    function Fail([string]$label, [string]$text) {
        Problem $label $text
        $reasons.Add($text)
    }

    Say ''
    Say "$($b.name)   expected [$scopeLabel]: $($b.expected)"

    $actual = $null
    if ($sameScope.Contains($b.name)) { $actual = $sameScope[$b.name].Expanded }
    $shadow = $null
    if ($otherScope.Contains($b.name)) { $shadow = $otherScope[$b.name].Expanded }

    if ($null -eq $actual -and $null -eq $shadow) {
        Fail $scopeLabel "$($b.name) is NOT SET (expected '$($b.expected)')"
        return $result
    }
    if ($null -eq $actual) {
        $result.Found = "$shadow  (set at $otherLabel level only)"
        Fail $scopeLabel "$($b.name) is not set at $scopeLabel level; it is only set at $otherLabel level to '$shadow' (expected '$($b.expected)' at $scopeLabel level)"
        $result.Fix = $fix + " Remove the $otherLabel-level $($b.name) if it is wrong."
        return $result
    }

    $result.Found = $actual
    if ((Normalize-Dir $actual) -eq $want) {
        Say "  ok       $scopeLabel value matches the baseline"
    } else {
        Fail $scopeLabel "$($b.name) is '$actual' but the baseline is '$($b.expected)'"
    }
    if ($null -ne $shadow) {
        if ($otherLabel -eq 'User') {
            # A User value overrides the System one for this user.
            if ((Normalize-Dir $shadow) -ne $want) {
                $result.Found = "$shadow  (User-level value overrides System '$actual')"
                Fail $otherLabel "$($b.name) is also set at User level to '$shadow', which OVERRIDES the System value for this user"
                $result.Fix = $fix + " Also delete the User-level $($b.name) (Windows > Edit environment variables for your account)."
            } else {
                Note "$($b.name) is also set at User level (same value as the baseline)."
            }
        } else {
            Note "$($b.name) is also set at System level to '$shadow'."
        }
    }

    # What NX will actually see in a new session: User overrides System.
    $effective = if ($userVars.Contains($b.name)) { $userVars[$b.name].Expanded } else { $actual }
    $folder = $effective.Trim().Trim('"')
    switch (Get-PathState $folder) {
        'missing' { Fail $scopeLabel "$($b.name) points at a folder that does not exist: $effective" }
        'file'    { Fail $scopeLabel "$($b.name) points at a file, not a folder: $effective" }
        'unknown' { Note "$($b.name) folder could not be checked (access denied): $effective" }
        'dir' {
            foreach ($rel in @($b.mustContain)) {
                $full = Join-Path $folder $rel
                if ((Get-PathState $full) -eq 'missing') {
                    Fail $scopeLabel "$($b.name) folder is missing '$rel' (expected $full) - the install looks incomplete"
                    if ($reasons.Count -gt 0 -and $result.Fix -eq $fix) {
                        $result.Fix = "Reinstall/repair the software that provides $folder (missing '$rel'), or point $($b.name) at a working install."
                    }
                } else {
                    Say "  ok       contains $rel"
                }
            }
        }
    }
    return $result
}

if (-not $BaselineFile) { $BaselineFile = Join-Path $OutDir 'nx-baseline.json' }
if (-not (Test-Path -LiteralPath $BaselineFile)) {
    Say "  Skipped - baseline file not found: $BaselineFile"
} else {
    $baseline = Get-Content -LiteralPath $BaselineFile -Raw | ConvertFrom-Json
    Say "  Baseline: $BaselineFile"
    $BaselineChecked = $true
    foreach ($b in $baseline.variables) {
        $r = Test-BaselineVar $b
        $BaselineResults.Add([pscustomobject]$r)
    }
    Say ''
    foreach ($r in $BaselineResults) {
        $status = if ($r.Reasons.Count -eq 0) { 'PASS' } else { 'FAIL' }
        Say ("  {0,-11} {1}" -f $r.Name, $status)
    }
}
$ProblemsAfterBaseline = $Problems.Count
$OtherProblems = @()
for ($i = 0; $i -lt $Problems.Count; $i++) {
    if ($i -lt $ProblemsBeforeBaseline -or $i -ge $ProblemsAfterBaseline) { $OtherProblems += $Problems[$i] }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
# From here on the verdict goes to the console AND to $SummaryLines, which is put
# at the TOP of the saved report (the detailed log stays below it).
$SummaryLines = New-Object System.Collections.Generic.List[string]
function Say([string]$text) { Write-Host $text; $SummaryLines.Add($text) }
function Say-Color([string]$text, [string]$color) { Write-Host $text -ForegroundColor $color; $SummaryLines.Add($text) }

$failed = @($BaselineResults | Where-Object { $_.Reasons.Count -gt 0 })
Say ''; Say ('#' * 70)
if (-not $BaselineChecked) {
    Say-Color 'NX VARIABLES: NOT CHECKED (baseline file not found)' 'Yellow'
} elseif ($failed.Count -eq 0) {
    Say-Color ("NX VARIABLES: PASS  -  all {0} are correct ({1})" -f $BaselineResults.Count,
               (($BaselineResults | ForEach-Object { $_.Name }) -join ', ')) 'Green'
} else {
    Say-Color ("NX VARIABLES: FAIL  -  {0} of {1} wrong" -f $failed.Count, $BaselineResults.Count) 'Red'
    foreach ($r in $failed) {
        Say ''
        Say-Color "  WRONG: $($r.Name)" 'Red'
        Say "     found    : $($r.Found)"
        Say "     expected : $($r.Expected)   [$($r.Scope)]"
        foreach ($why in $r.Reasons) { Say "     problem  : $why" }
        Say "     fix      : $($r.Fix)"
    }
    $passed = @($BaselineResults | Where-Object { $_.Reasons.Count -eq 0 })
    if ($passed.Count -gt 0) {
        Say ''
        Say "  Correct: $(($passed | ForEach-Object { $_.Name }) -join ', ')"
    }
}
Say ('#' * 70)

Say ''
if ($OtherProblems.Count -eq 0) {
    Say 'OTHER CHECKS: no other problems found in the User or System variables.'
} else {
    Say "OTHER CHECKS: $($OtherProblems.Count) other problem(s) (not part of the NX baseline):"
    foreach ($p in $OtherProblems) { Say "  - $p" }
    Say 'User-level variables can be fixed in Windows > Edit environment variables for'
    Say 'your account; System-level variables need an administrator.'
}

$exitCode = if ($BaselineChecked -and $failed.Count -gt 0) { 2 } else { 0 }

try {
    $top = New-Object System.Collections.Generic.List[string]
    $top.Add("ENVIRONMENT VARIABLE REPORT - SUMMARY  ($env:COMPUTERNAME / $env:USERNAME, $(Get-Date))")
    $top.AddRange($SummaryLines)
    $top.Add('')
    $top.Add(('-' * 70))
    $top.Add('FULL DETAILS BELOW')
    $top.Add(('-' * 70))
    $top.Add('')
    $final = New-Object System.Collections.Generic.List[string]
    $final.AddRange($top)
    $final.AddRange($Lines)
    Set-Content -LiteralPath $Report -Value $final -Encoding UTF8
    Write-Host ''; Write-Host "Report saved to: $Report"
} catch {
    Write-Host "(Could not save the report file: $($_.Exception.Message))"
}

Wait-BeforeClose
exit $exitCode
