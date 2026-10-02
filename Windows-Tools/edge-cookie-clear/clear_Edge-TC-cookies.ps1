<#
.SYNOPSIS
    Clears Microsoft Edge cookies whose site matches a search filter
    (same as edge://settings/privacy/cookies/AllCookies?searchSubpage=local).

.DESCRIPTION
    Closes Edge (the cookie database is locked while it runs), deletes every
    cookie whose host contains the filter text in each Edge profile, then
    relaunches Edge. Other cookies, passwords, history and bookmarks are untouched.

    Edge stores cookies in a SQLite database, so this calls the winsqlite3.dll
    that ships with Windows 10/11. No extra software is required.

.PARAMETER Filter
    Text matched against the cookie host (substring, case-insensitive). Default: local

.PARAMETER NoRestart
    Do not relaunch Edge after clearing (Edge is relaunched by default).
#>
[CmdletBinding()]
param(
    [string]$Filter = 'local',
    [switch]$NoRestart
)

$ErrorActionPreference = 'Stop'

$userData = Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\User Data'
if (-not (Test-Path $userData)) {
    Write-Host "Edge user data folder not found: $userData" -ForegroundColor Red
    exit 1
}

# winsqlite3.dll is built into Windows 10/11
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class WinSqlite {
    [DllImport("winsqlite3.dll", CharSet = CharSet.Unicode)]
    static extern int sqlite3_open16(string file, out IntPtr db);
    [DllImport("winsqlite3.dll")]
    static extern int sqlite3_exec(IntPtr db, byte[] sql, IntPtr cb, IntPtr arg, out IntPtr err);
    [DllImport("winsqlite3.dll")]
    static extern int sqlite3_changes(IntPtr db);
    [DllImport("winsqlite3.dll")]
    static extern int sqlite3_busy_timeout(IntPtr db, int ms);
    [DllImport("winsqlite3.dll")]
    static extern int sqlite3_close(IntPtr db);

    // Deletes cookies whose host contains 'filter'; returns the number removed
    public static int DeleteCookies(string path, string filter) {
        IntPtr db;
        if (sqlite3_open16(path, out db) != 0) { sqlite3_close(db); throw new Exception("Cannot open " + path); }
        try {
            sqlite3_busy_timeout(db, 10000);
            string esc = filter.Replace("\\", "\\\\").Replace("%", "\\%").Replace("_", "\\_").Replace("'", "''");
            string sql = "DELETE FROM cookies WHERE host_key LIKE '%" + esc + "%' ESCAPE '\\'";
            IntPtr err;
            if (sqlite3_exec(db, Encoding.UTF8.GetBytes(sql + "\0"), IntPtr.Zero, IntPtr.Zero, out err) != 0)
                throw new Exception("SQLite error deleting cookies from " + path);
            return sqlite3_changes(db);
        } finally { sqlite3_close(db); }
    }
}
'@

# Close Edge so the cookie files are unlocked
$edge = Get-Process -Name msedge -ErrorAction SilentlyContinue
if ($edge) {
    Write-Host 'Closing Edge...'
    $edge | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Default, Profile 1, Profile 2, Guest Profile, ...
$profiles = Get-ChildItem -Path $userData -Directory |
    Where-Object { $_.Name -eq 'Default' -or $_.Name -like 'Profile *' -or $_.Name -eq 'Guest Profile' }

$total = 0
foreach ($p in $profiles) {
    # Current Edge keeps cookies under Network\; older versions kept them in the profile root
    foreach ($db in @((Join-Path $p.FullName 'Network\Cookies'), (Join-Path $p.FullName 'Cookies'))) {
        if (-not (Test-Path $db)) { continue }
        try {
            $count = [WinSqlite]::DeleteCookies($db, $Filter)
            Write-Host "$($p.Name): removed $count cookie(s)"
            $total += $count
        }
        catch {
            Write-Host "Failed on $db : $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

Write-Host "Done. Removed $total cookie(s) matching '$Filter'." -ForegroundColor Green

if (-not $NoRestart) {
    Write-Host 'Restarting Edge...'
    Start-Process msedge
}
