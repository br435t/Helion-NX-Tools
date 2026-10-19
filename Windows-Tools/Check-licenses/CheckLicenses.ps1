# Lists who is using each license feature on the NX license server (NX91110,
# nx_design_token, teamcenter_*, ...). Features with nobody using them are left
# out. The list is saved to <repo>\output\license_status_latest.txt and the full
# lmutil output to <repo>\output\license_status_raw.txt (both overwritten each run).
#
# Output starts with a report header (title, server, date and time), then the
# modules in use by the Windows account running the script, then one block per
# feature in use, one user per line:
#   NX license usage report
#   Server: 28000@USANTPVWTCOR001.HE.local
#   Generated: 2026-10-17 08:55:12
#   ----------------------------------------
#
#   In use by br435t:
#       teamcenter_author
#       nx_design_token  nx_partitions  (2 licenses)
#
#   NX91110 (30/52)
#       sa562b
#       swilliams
#
#   nx_design_token (133/300)
#       sa562b
param(
    [string]$Server = '28000@USANTPVWTCOR001.HE.local',
    [string]$LmUtil = 'C:\SPLM\NX\NX2506\UGFLEXLM\lmutil',
    [string]$InputFile = ''      # parse a saved lmstat output instead of querying the server
)

$outDir = Join-Path $PSScriptRoot '..\..\output'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$log    = Join-Path (Resolve-Path $outDir) 'license_status_latest.txt'
$rawLog = Join-Path (Resolve-Path $outDir) 'license_status_raw.txt'

if ($InputFile) {
    $raw = Get-Content -Path $InputFile | ForEach-Object { "$_" }
} else {
    $raw = & $LmUtil lmstat -a -c $Server 2>&1 | ForEach-Object { "$_" }
}

# A feature section starts at "Users of <feature>:  (Total of N licenses issued;
# Total of M licenses in use)". Checkout lines inside it look like
#   <user> <host> <display> [<module>] (v2026.06) (<server>/28000 <handle>), start ...
# where <module> is present on some features (e.g. nx_design_token).
$me = $env:USERNAME
$mine = New-Object System.Collections.Generic.List[string]   # this user's checkouts
$features = [ordered]@{}     # feature -> @{ Issued; InUse; Users }
$current = $null
foreach ($line in $raw) {
    if ($line -match '^Users of (\S+):\s+\(Total of (\d+) licenses? issued;\s+Total of (\d+) licenses? in use') {
        $current = @{ Issued = $Matches[2]; InUse = $Matches[3]
                      Users = (New-Object System.Collections.Generic.List[string]) }
        $currentName = $Matches[1]
        $features[$Matches[1]] = $current
        continue
    }
    if ($line -match '^Users of ') { $current = $null; continue }   # error / other format
    if ($current -and $line -match '^\s+(\S+)\s+\S+\s+\S+\s+(?:(\S+)\s+)?\(v[\d.]+\)') {
        $user = $Matches[1]; $module = $Matches[2]
        if (-not $current.Users.Contains($user)) { $current.Users.Add($user) }
        if ($user -ieq $me) {
            $n = 1
            if ($line -match ',\s*(\d+) licenses?\s*$') { $n = [int]$Matches[1] }
            $entry = $currentName
            if ($module) { $entry += '  ' + $module }
            if ($n -gt 1) { $entry += "  ($n licenses)" }
            $mine.Add($entry)
        }
    }
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('NX license usage report')
$lines.Add("Server: $Server")
$lines.Add('Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
$lines.Add('-' * 40)
$lines.Add('')
$lines.Add("In use by ${me}:")
if ($mine.Count -eq 0) { $lines.Add('    (nothing)') }
foreach ($m in $mine) { $lines.Add('    ' + $m) }
$lines.Add('')
$firstFeature = $true
foreach ($name in $features.Keys) {
    $f = $features[$name]
    if ($f.Users.Count -eq 0) { continue }
    if (-not $firstFeature) { $lines.Add('') }
    $firstFeature = $false
    $lines.Add(('{0} ({1}/{2})' -f $name, $f.InUse, $f.Issued))
    foreach ($u in $f.Users) { $lines.Add('    ' + $u) }
}

if (-not $features.Count) {
    # Server unreachable or an error: show it, and keep the last good files.
    Write-Host "No 'Users of' sections in the lmutil output, so the saved reports were left as they were."
    Write-Host "lmutil said:"
    $raw | ForEach-Object { Write-Host $_ }
    exit 1
}

if (-not $InputFile) { Set-Content -Path $rawLog -Value $raw -Encoding UTF8 }

$lines | ForEach-Object { Write-Host $_ }
Write-Host ""
if ($InputFile) {
    Write-Host "(-InputFile test run: nothing was saved)"
} else {
    Set-Content -Path $log -Value $lines -Encoding ASCII
    Write-Host "Saved users to $log"
    Write-Host "Saved full output to $rawLog"
}
