#!/usr/bin/env pwsh
[CmdletBinding()]
param([switch]$Check)
$arguments = @('-B', (Join-Path $PSScriptRoot 'sync_generated.py'), '--root', (Split-Path -Parent $PSScriptRoot))
if ($Check) { $arguments += '--check' }
& python @arguments
exit $LASTEXITCODE
