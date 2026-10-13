# Extracts NX_Open_MCP.zip to MCP\ and registers it as the "nxopen" MCP server
# in the repo-root .mcp.json (git-ignored, machine-specific). Called by setup.bat.
# Safe to re-run: an existing MCP\ folder is reused, and .mcp.json is merged
# (other servers in it are kept).
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$VenvPython
)
$ErrorActionPreference = 'Stop'

$zip     = Join-Path $Root 'NX_Open_MCP.zip'
$mcpDir  = Join-Path $Root 'MCP'
$server  = Join-Path $mcpDir 'nxopen_python_ref\nxopen_mcp.py'
$cfgPath = Join-Path $Root '.mcp.json'

# --- 1. Extract the zip (its single top-level "NX Open" folder becomes MCP) ---
if (Test-Path $server) {
    Write-Host '  MCP folder already extracted - reusing it.'
} else {
    if (-not (Test-Path $zip)) { throw "Missing $zip" }
    $tmp = Join-Path $Root 'MCP_extract_tmp'
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    if (Test-Path $mcpDir) { Remove-Item $mcpDir -Recurse -Force }
    Write-Host '  Extracting NX_Open_MCP.zip (about 4000 files) ...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $tmp)
    $inner = Join-Path $tmp 'NX Open'
    if (-not (Test-Path $inner)) { $inner = $tmp }
    Move-Item $inner $mcpDir
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    if (-not (Test-Path $server)) { throw "Extracted MCP has no $server" }
}

# --- 2. Register the server in .mcp.json (venv python has the `mcp` package) ---
$cfg = $null
if (Test-Path $cfgPath) {
    try { $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json } catch { $cfg = $null }
}
if ($null -eq $cfg) { $cfg = [pscustomobject]@{} }
if ($null -eq $cfg.PSObject.Properties['mcpServers']) {
    $cfg | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
}
$entry = [pscustomobject]@{ command = $VenvPython; args = @($server) }
if ($null -eq $cfg.mcpServers.PSObject.Properties['nxopen']) {
    $cfg.mcpServers | Add-Member -NotePropertyName nxopen -NotePropertyValue $entry
} else {
    $cfg.mcpServers.nxopen = $entry
}
$json = $cfg | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($cfgPath, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "  Registered 'nxopen' MCP server in $cfgPath"
