# Author:  br435t
# Created: 2026-10-23
# Updates this folder to a tagged release of Helion-NX-Tools from GitHub.
#
# Start it with update.bat (double-click). It uses only what Windows already has:
# PowerShell 5.1 and .NET. No Python, no git.
#
# What it does
#   1. Lists the GitHub releases (for example "v1.0.0 Release", "v0.9.5 Public Beta") and lets you pick one.
#   2. Downloads that release. A GitHub release zip holds only the files that are tracked in git, so
#      anything git-ignored (.venv, output, my_scripts\*.py, MCP, caches ...) is never downloaded.
#   3. Saves your CURRENT copy of every file the release will overwrite to a zip in C:\Temp, and tells
#      you where it is. If that backup cannot be made, nothing is changed.
#   4. Overwrites the files. It never deletes anything: files that only exist on your machine stay.
#
# Options (all optional; the defaults are what update.bat uses):
#   -Tag v1.0.0         choose a release without the menu (a tag or a release name)
#   -Yes                do not ask any Y/N question
#   -Root <folder>      folder to update (default: the folder this script is in)
#   -BackupDir <folder> where the backup zip goes (default: C:\Temp)
#   -DryRun             download and show what would change, but change nothing
#   -Repo owner/name    GitHub repository (default: br435t/Helion-NX-Tools)
#   -ZipPath <file>     use a local release zip instead of downloading (for testing)
param(
    [string]$Tag = '',
    [switch]$Yes,
    [string]$Root = '',
    [string]$BackupDir = 'C:\Temp',
    [switch]$DryRun,
    [string]$Repo = 'br435t/Helion-NX-Tools',
    [string]$ZipPath = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

# The folder this script lives in (captured here: inside a function $PSScriptRoot is not reliable).
$script:HereDir = $PSScriptRoot

# Never written by an update, whatever the release contains.
$script:ProtectedTop = @('.git', 'output', '.installed_version')


# --------------------------------------------------------------------------- network
function Initialize-Network {
    # GitHub needs TLS 1.2; old Windows PowerShell defaults to older protocols.
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    try {
        # Corporate networks: go through the system proxy with the signed-in user's credentials.
        [Net.WebRequest]::DefaultWebProxy.Credentials = [Net.CredentialCache]::DefaultNetworkCredentials
    } catch { }
}

function Get-HttpProblem {
    param($Exception, [string]$What)
    $resp = $null
    try { $resp = $Exception.Response } catch { }
    if ($resp -ne $null) {
        $code = [int]$resp.StatusCode
        if ($code -eq 403 -or $code -eq 429) {
            $when = ''
            try {
                $reset = [long]($resp.Headers['X-RateLimit-Reset'])
                $when = ' It resets at ' + [DateTimeOffset]::FromUnixTimeSeconds($reset).LocalDateTime.ToString('HH:mm') + '.'
            } catch { }
            return "GitHub refused the request for $What (HTTP $code). Anonymous use is limited to 60 requests per hour per network address, and this network address has probably used them up.$when Try again later."
        }
        if ($code -eq 404) { return "GitHub says $What does not exist (HTTP 404). Check the repository name." }
        if ($code -eq 407) { return "The proxy needs sign-in (HTTP 407) for $What. Ask IT, or try again from a network without a proxy." }
        return "GitHub answered HTTP $code for $What."
    }
    return "Could not reach GitHub for ${What}: $($Exception.Message). Check your network connection (or VPN/proxy) and try again."
}


# --------------------------------------------------------------------------- releases
function Get-Releases {
    param([string]$Repo)
    Initialize-Network
    $headers = @{ 'User-Agent' = 'Helion-NX-Tools-update'; 'Accept' = 'application/vnd.github+json' }
    try {
        $raw = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases?per_page=100" -Headers $headers -TimeoutSec 30
    } catch {
        throw (Get-HttpProblem $_.Exception 'the list of releases')
    }
    $list = @()
    foreach ($r in @($raw)) {
        if ($r.draft) { continue }
        $date = ''
        try {
            $d = $r.published_at
            if ($d -isnot [datetime]) { $d = [datetime]::Parse([string]$d, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind) }
            $date = $d.ToString('yyyy-MM-dd')
        } catch { }
        $name = [string]$r.name
        if (-not $name.Trim()) { $name = [string]$r.tag_name }
        $list += [pscustomobject]@{
            Name = $name.Trim(); Tag = [string]$r.tag_name; Pre = [bool]$r.prerelease
            Date = $date; ZipUrl = [string]$r.zipball_url; Sort = [string]$r.published_at
        }
    }
    return @($list | Sort-Object Sort -Descending)
}

function Format-ReleaseMenu {
    param($Releases, [string]$InstalledTag)
    $Releases = @($Releases)
    $width = ($Releases | ForEach-Object { $_.Name.Length } | Measure-Object -Maximum).Maximum
    $lines = @()
    for ($i = 0; $i -lt $Releases.Count; $i++) {
        $r = $Releases[$i]
        $note = @()
        if ($r.Pre) { $note += 'pre-release' }
        if ($InstalledTag -and $r.Tag -eq $InstalledTag) { $note += 'INSTALLED' }
        $lines += ('  [{0}] {1}  {2}  {3}{4}' -f ($i + 1), $r.Name.PadRight($width), $r.Tag.PadRight(8), $r.Date,
            $(if ($note.Count) { '   ' + ($note -join ', ') } else { '' }))
    }
    return $lines
}

function Read-ReleaseChoice {
    param($Releases, [string]$InstalledTag)
    $Releases = @($Releases)
    Write-Host ''
    Write-Host 'Available releases (newest first):'
    foreach ($line in (Format-ReleaseMenu $Releases $InstalledTag)) { Write-Host $line }
    Write-Host ''
    while ($true) {
        $answer = (Read-Host ('Choose a release [1-{0}], press Enter for 1, or Q to quit' -f $Releases.Count)).Trim()
        if ($answer -eq '') { return $Releases[0] }
        if ($answer -match '^[Qq]$') { return $null }
        $n = 0
        if ([int]::TryParse($answer, [ref]$n) -and $n -ge 1 -and $n -le $Releases.Count) { return $Releases[$n - 1] }
        Write-Host 'Please type a number from the list, or Q.'
    }
}

function Find-Release {
    param($Releases, [string]$Wanted)
    foreach ($r in @($Releases)) {
        if ($r.Tag -ieq $Wanted -or $r.Name -ieq $Wanted) { return $r }
    }
    return $null
}


# --------------------------------------------------------------------------- the zip
function Test-Protected {
    param([string]$Rel)
    $top = ($Rel -split '[\\/]')[0]
    foreach ($p in $script:ProtectedTop) { if ($top -ieq $p) { return $true } }
    return $false
}

function Get-UpdatePlan {
    # One item per file in the zip: where it goes and whether it may be written.
    # Status: ok | protected (never touched) | refused (would land outside the folder).
    param([string]$ZipFile, [string]$Root)
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $items = New-Object System.Collections.ArrayList
    $zip = [IO.Compression.ZipFile]::OpenRead($ZipFile)
    try {
        $files = @($zip.Entries | Where-Object { $_.FullName -and -not $_.FullName.EndsWith('/') })
        # GitHub puts everything under one top folder (owner-repo-sha); drop it.
        $top = ''
        if ($files.Count -gt 0) {
            $first = $files[0].FullName.Split('/')[0]
            $allUnder = (@($files | Where-Object { -not $_.FullName.StartsWith($first + '/') })).Count -eq 0
            if ($allUnder) { $top = $first + '/' }
        }
        foreach ($e in $files) {
            $rel = $e.FullName
            if ($top) { $rel = $rel.Substring($top.Length) }
            if (-not $rel) { continue }
            $status = 'ok'
            $target = ''
            try {
                $target = [IO.Path]::GetFullPath((Join-Path $rootFull ($rel -replace '/', '\')))
                if ($rel -match '^(/|\\|[A-Za-z]:)' -or -not $target.StartsWith($rootFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
                    $status = 'refused'
                }
            } catch { $status = 'refused' }
            if ($status -eq 'ok' -and (Test-Protected $rel)) { $status = 'protected' }
            $exists = $false
            if ($status -eq 'ok') { $exists = Test-Path -LiteralPath $target -PathType Leaf }
            [void]$items.Add([pscustomobject]@{ Name = $e.FullName; Rel = $rel; Target = $target; Status = $status; Exists = $exists })
        }
    } finally { $zip.Dispose() }
    return @($items)
}

function Test-IsZip {
    param([string]$File)
    if (-not (Test-Path -LiteralPath $File)) { return $false }
    $fs = [IO.File]::OpenRead($File)
    try {
        if ($fs.Length -lt 100) { return $false }
        $b = New-Object byte[] 2
        [void]$fs.Read($b, 0, 2)
        return ($b[0] -eq 0x50 -and $b[1] -eq 0x4B)      # "PK"
    } finally { $fs.Dispose() }
}


# --------------------------------------------------------------------------- backup
function Resolve-BackupDir {
    # The wanted folder if we can write there, else %TEMP%, else $null.
    param([string]$Preferred)
    foreach ($dir in @($Preferred, $env:TEMP)) {
        if (-not $dir) { continue }
        try {
            if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
            $probe = Join-Path $dir ('.write_test_' + [guid]::NewGuid().ToString('N'))
            [IO.File]::WriteAllText($probe, 'x')
            Remove-Item -LiteralPath $probe -Force
            return @{ Path = $dir; FellBack = ($dir -ne $Preferred) }
        } catch { }
    }
    return $null
}

function New-BackupZip {
    # Zips the user's current copy of every file the update will overwrite. Throws on any problem
    # (and removes the half-made zip), so the caller can stop before changing anything.
    param($Items, [string]$BackupPath, [string]$InfoText)
    $zip = $null
    try {
        $zip = [IO.Compression.ZipFile]::Open($BackupPath, [IO.Compression.ZipArchiveMode]::Create)
        foreach ($it in $Items) {
            [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $it.Target, $it.Rel, [IO.Compression.CompressionLevel]::Optimal)
        }
        $entry = $zip.CreateEntry('_BACKUP_INFO.txt')
        $w = New-Object IO.StreamWriter($entry.Open(), (New-Object Text.UTF8Encoding($false)))
        try { $w.Write($InfoText) } finally { $w.Dispose() }
    } catch {
        if ($zip -ne $null) { $zip.Dispose(); $zip = $null }
        if (Test-Path -LiteralPath $BackupPath) { Remove-Item -LiteralPath $BackupPath -Force -ErrorAction SilentlyContinue }
        throw
    } finally {
        if ($zip -ne $null) { $zip.Dispose() }
    }
}


# --------------------------------------------------------------------------- overwrite
function Test-NeedsCrlf {
    param([string]$Rel)
    return ($Rel -match '\.(bat|cmd|ps1)$')
}

function ConvertTo-CrlfBytes {
    # GitHub zips use LF; cmd.exe can mishandle LF-only batch files (labels, goto), so these get CRLF.
    param([byte[]]$Bytes)
    $out = New-Object IO.MemoryStream
    $prev = 0
    foreach ($b in $Bytes) {
        if ($b -eq 10 -and $prev -ne 13) { $out.WriteByte(13) }
        $out.WriteByte($b)
        $prev = $b
    }
    return , $out.ToArray()
}

function Expand-Release {
    # Writes every item with Status ok, overwriting. A file that fails is recorded and the rest go on.
    param([string]$ZipFile, $Items)
    $result = @{ Written = 0; New = 0; Failed = (New-Object System.Collections.ArrayList) }
    $zip = [IO.Compression.ZipFile]::OpenRead($ZipFile)
    try {
        $byName = @{}
        foreach ($e in $zip.Entries) { $byName[$e.FullName] = $e }
        foreach ($it in $Items) {
            if ($it.Status -ne 'ok') { continue }
            try {
                $dir = Split-Path -Parent $it.Target
                if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
                if (Test-Path -LiteralPath $it.Target) {
                    $f = Get-Item -LiteralPath $it.Target -Force
                    if ($f.IsReadOnly) { $f.IsReadOnly = $false }
                }
                $entry = $byName[$it.Name]
                if (Test-NeedsCrlf $it.Rel) {
                    $ms = New-Object IO.MemoryStream
                    $s = $entry.Open()
                    try { $s.CopyTo($ms) } finally { $s.Dispose() }
                    [IO.File]::WriteAllBytes($it.Target, (ConvertTo-CrlfBytes $ms.ToArray()))
                } else {
                    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $it.Target, $true)
                }
                try { (Get-Item -LiteralPath $it.Target -Force).LastWriteTime = $entry.LastWriteTime.LocalDateTime } catch { }
                $result.Written++
                if (-not $it.Exists) { $result.New++ }
            } catch {
                [void]$result.Failed.Add(@{ Rel = $it.Rel; Error = $_.Exception.Message })
            }
        }
    } finally { $zip.Dispose() }
    return $result
}


# --------------------------------------------------------------------------- installed version
function Get-InstalledVersion {
    param([string]$Root)
    $f = Join-Path $Root '.installed_version'
    if (Test-Path -LiteralPath $f) {
        try { return (Get-Content -LiteralPath $f -Raw | ConvertFrom-Json) } catch { }
    }
    return $null
}

function Set-InstalledVersion {
    param([string]$Root, [string]$Tag, [string]$Name)
    $o = [ordered]@{ tag = $Tag; name = $Name; installed = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') }
    [IO.File]::WriteAllText((Join-Path $Root '.installed_version'), ($o | ConvertTo-Json), (New-Object Text.UTF8Encoding($false)))
}

function Read-YesNo {
    param([string]$Question)
    while ($true) {
        $a = (Read-Host "$Question (Y/N)").Trim()
        if ($a -match '^[Yy]') { return $true }
        if ($a -match '^[Nn]') { return $false }
    }
}

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -ge 1MB) { return ('{0:N1} MB' -f ($Bytes / 1MB)) }
    return ('{0:N0} KB' -f [Math]::Max(1, [Math]::Round($Bytes / 1KB)))
}


# --------------------------------------------------------------------------- main
function Invoke-Update {
    $rootArg = $Root
    if (-not $rootArg) { $rootArg = $script:HereDir }
    if (-not $rootArg) { $rootArg = (Get-Location).Path }
    $rootFull = [IO.Path]::GetFullPath($rootArg).TrimEnd('\')

    Write-Host ''
    Write-Host '=== Helion NX Tools: update ==='
    Write-Host "Folder:    $rootFull"
    $installed = Get-InstalledVersion $rootFull
    $installedTag = ''
    if ($installed) {
        $installedTag = [string]$installed.tag
        Write-Host ("Installed: {0}  ({1})" -f $installedTag, $installed.name)
    } else {
        Write-Host 'Installed: unknown (no .installed_version file yet)'
    }

    if ((Test-Path -LiteralPath (Join-Path $rootFull '.git')) -and -not $Yes) {
        Write-Host ''
        Write-Host 'This folder is a git clone. "git pull" is the normal way to update a clone; this'
        Write-Host 'updater will overwrite the files and git will then list any that changed as local changes.'
        if (-not (Read-YesNo 'Update this clone anyway?')) { Write-Host 'Nothing changed.'; return 0 }
    }

    # ---- which release
    $label = $Tag
    $zipSource = $ZipPath
    $tmpDir = Join-Path ([IO.Path]::GetTempPath()) ('helion_update_' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
    try {
        if ($ZipPath) {
            if (-not $label) { $label = 'local zip' }
            $releaseName = $label
        } else {
            Write-Host ''
            Write-Host 'Looking up releases on GitHub ...'
            $releases = @(Get-Releases $Repo)
            if ($releases.Count -eq 0) { Write-Host 'GitHub has no releases for this repository.'; return 1 }
            if ($Tag) {
                $chosen = Find-Release $releases $Tag
                if (-not $chosen) {
                    Write-Host "No release called '$Tag'. Releases are:"
                    foreach ($line in (Format-ReleaseMenu $releases $installedTag)) { Write-Host $line }
                    return 1
                }
            } else {
                $chosen = Read-ReleaseChoice $releases $installedTag
                if (-not $chosen) { Write-Host 'Nothing changed.'; return 0 }
            }
            $label = $chosen.Tag
            $releaseName = $chosen.Name
        }

        # ---- backup location, shown before anything happens
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $fromTag = $(if ($installedTag) { $installedTag } else { 'unknown' })
        $backupInfo = Resolve-BackupDir $BackupDir
        if (-not $backupInfo -and -not $DryRun) {
            Write-Host "Could not write a backup to '$BackupDir' or to your temp folder, so nothing was changed."
            return 1
        }
        $safe = { param($s) ($s -replace '[\\/:*?"<>| ]', '_') }
        $backupPath = ''
        if ($backupInfo) {
            $backupPath = Join-Path $backupInfo.Path ('Helion-NX-Tools_backup_{0}_to_{1}_{2}.zip' -f (& $safe $fromTag), (& $safe $label), $stamp)
        }

        Write-Host ''
        Write-Host "Selected:  $releaseName  ($label)"
        if ($backupInfo -and $backupInfo.FellBack) { Write-Host "NOTE: could not use $BackupDir, so the backup goes to your temp folder instead." }
        if ($backupPath) { Write-Host "Backup of the files that will be overwritten will be saved to:"; Write-Host "    $backupPath" }
        if (-not $Yes -and -not $DryRun) {
            Write-Host ''
            if (-not (Read-YesNo "Download $label and overwrite the files in $rootFull?")) { Write-Host 'Nothing changed.'; return 0 }
        }

        # ---- download
        if (-not $zipSource) {
            $zipSource = Join-Path $tmpDir 'release.zip'
            Write-Host ''
            Write-Host "Downloading $label ..."
            Initialize-Network
            $old = $ProgressPreference
            $ProgressPreference = 'SilentlyContinue'      # the progress bar makes Windows PowerShell downloads very slow
            try {
                Invoke-WebRequest -Uri $chosen.ZipUrl -OutFile $zipSource -UseBasicParsing -Headers @{ 'User-Agent' = 'Helion-NX-Tools-update' } -TimeoutSec 300
            } catch {
                throw (Get-HttpProblem $_.Exception "the download of $label")
            } finally { $ProgressPreference = $old }
        }
        if (-not (Test-IsZip $zipSource)) {
            Write-Host 'The downloaded file is not a valid zip, so nothing was changed.'
            return 1
        }
        Write-Host ("Downloaded {0}." -f (Format-Size (Get-Item -LiteralPath $zipSource).Length))

        # ---- plan
        $plan = @(Get-UpdatePlan $zipSource $rootFull)
        $toWrite = @($plan | Where-Object { $_.Status -eq 'ok' })
        $toBackup = @($toWrite | Where-Object { $_.Exists })
        $refused = @($plan | Where-Object { $_.Status -eq 'refused' })
        $reqBefore = ''
        $reqFile = Join-Path $rootFull 'requirements.txt'
        if (Test-Path -LiteralPath $reqFile) { $reqBefore = (Get-FileHash -LiteralPath $reqFile -Algorithm SHA256).Hash }
        Write-Host ("Release has {0} files: {1} will overwrite an existing file, {2} are new here." -f $toWrite.Count, $toBackup.Count, ($toWrite.Count - $toBackup.Count))
        if ($refused.Count) { Write-Host ("Skipping {0} entries that would land outside this folder (not safe)." -f $refused.Count) }

        if ($DryRun) {
            Write-Host ''
            Write-Host 'Dry run: nothing was backed up or changed.'
            return 0
        }

        # ---- backup first; stop if it fails
        Write-Host ''
        Write-Host 'Backing up the files that will be overwritten ...'
        $info = @(
            'Backup made by update.bat before updating Helion-NX-Tools',
            ('When:        ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')),
            ('Folder:      ' + $rootFull),
            ('From:        ' + $fromTag),
            ('To:          ' + $releaseName + '  (' + $label + ')'),
            ('Files saved: ' + $toBackup.Count + '  (your copies of the files that the update overwrote)'),
            '',
            'To go back: open PowerShell and run',
            ('  Expand-Archive -LiteralPath "' + $backupPath + '" -DestinationPath "' + $rootFull + '" -Force'),
            'This restores those files; it does not delete anything the update added.'
        ) -join "`r`n"
        try {
            New-BackupZip $toBackup $backupPath $info
        } catch {
            Write-Host ("The backup could not be completed ({0}), so NOTHING was changed." -f $_.Exception.Message)
            return 1
        }
        $backupSize = (Get-Item -LiteralPath $backupPath).Length

        # ---- overwrite
        Write-Host 'Updating files ...'
        $result = Expand-Release $zipSource $plan
        try { Set-InstalledVersion $rootFull $label $releaseName } catch { }

        $reqAfter = ''
        if (Test-Path -LiteralPath $reqFile) { $reqAfter = (Get-FileHash -LiteralPath $reqFile -Algorithm SHA256).Hash }

        Write-Host ''
        Write-Host "=== Update finished: $releaseName ($label) ==="
        Write-Host ("Files written: {0}   (new: {1})   Failed: {2}" -f $result.Written, $result.New, $result.Failed.Count)
        foreach ($f in $result.Failed) { Write-Host ("  FAILED {0}: {1}" -f $f.Rel, $f.Error) }
        Write-Host ''
        Write-Host 'Your previous files are saved in:'
        Write-Host "    $backupPath    ($(Format-Size $backupSize))"
        Write-Host '(Move it somewhere safe if you want to keep it; C:\Temp is not kept forever.)'
        Write-Host ''
        Write-Host 'Next steps:'
        Write-Host '  - Restart NX before you run the scripts again, so it reloads the updated files.'
        if ($reqBefore -ne $reqAfter) { Write-Host '  - requirements.txt changed: run setup.bat again to update the Python packages.' }
        if ($result.Failed.Count) {
            Write-Host '  - Some files could not be written (in use?). Close what is using them and run update.bat again.'
            return 2
        }
        return 0
    } catch {
        Write-Host ''
        Write-Host ("ERROR: " + $_.Exception.Message)
        return 1
    } finally {
        try { Remove-Item -LiteralPath $tmpDir -Recurse -Force -ErrorAction SilentlyContinue } catch { }
    }
}

# Run unless this file was dot-sourced (the tests do that to call the functions).
if ($MyInvocation.InvocationName -ne '.') {
    exit (Invoke-Update)
}
