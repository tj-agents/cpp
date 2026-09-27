#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$InstallDirectory = (Join-Path $env:LOCALAPPDATA 'cpp-agents/msvc'),
    [string]$SettingsPath = (Join-Path $env:APPDATA 'Code/User/settings.json')
)

$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'clangd-msvc.cmd'
if (!(Test-Path -LiteralPath $source -PathType Leaf)) { throw "The packaged launcher is missing: $source" }
# Plugin caches are versioned, so the editor must reference a stable per-user copy.
$launcher = Join-Path $InstallDirectory 'clangd-msvc.cmd'
if ($PSCmdlet.ShouldProcess($launcher, 'Install clangd MSVC launcher')) {
    New-Item -ItemType Directory -Path $InstallDirectory -Force | Out-Null
    # The repository stores text with LF; cmd.exe parses batch files reliably only with CRLF.
    $batch = [IO.File]::ReadAllText($source) -replace "`r?`n", "`r`n"
    [IO.File]::WriteAllText($launcher, $batch, [Text.UTF8Encoding]::new($false))
}

$desired = [ordered]@{ 'clangd.path' = $launcher; 'clangd.useScriptAsExecutable' = $true }
$text = if (Test-Path -LiteralPath $SettingsPath -PathType Leaf) { [IO.File]::ReadAllText($SettingsPath) } else { '{}' }
if ($text -match '(^|\s)//|/\*') {
    Write-Warning "$SettingsPath contains comments; add these VS Code user settings manually:"
    $desired | ConvertTo-Json | Write-Output
    return
}
$settings = if ($text.Trim()) { $text | ConvertFrom-Json -AsHashtable } else { [ordered]@{} }
foreach ($key in $desired.Keys) { $settings[$key] = $desired[$key] }
if ($PSCmdlet.ShouldProcess($SettingsPath, 'Set clangd.path and clangd.useScriptAsExecutable')) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $SettingsPath) -Force | Out-Null
    [IO.File]::WriteAllText($SettingsPath, ($settings | ConvertTo-Json -Depth 32), [Text.UTF8Encoding]::new($false))
}
Write-Output "clangd for MSVC: $launcher. Restart clangd or reload VS Code windows."
