#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Za-z][A-Za-z0-9_-]*$')]
    [ValidateLength(1, 64)]
    [string]$Name,
    [Parameter(Mandatory)]
    [string]$Destination,
    [ValidateSet(20, 23)]
    [int]$CppStandard = 23,
    [string]$FormatConfig,
    [string]$TidyConfig
)

$ErrorActionPreference = 'Stop'
if ($Name -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$') {
    throw 'The project name is a reserved Windows device name.'
}
$parent = Get-Item -LiteralPath $Destination -ErrorAction Stop
if (!$parent.PSIsContainer -or $parent.PSProvider.Name -ne 'FileSystem') {
    throw 'Destination must be an existing filesystem directory.'
}
$projectPath = Join-Path $parent.FullName $Name
if (Test-Path -LiteralPath $projectPath) { throw "Destination already exists: $projectPath" }

$configurations = @{}
foreach ($entry in @(@('.clang-format', $FormatConfig), @('.clang-tidy', $TidyConfig))) {
    if ($entry[1]) {
        $configuration = Get-Item -LiteralPath $entry[1] -ErrorAction Stop
        if ($configuration.PSIsContainer -or $configuration.PSProvider.Name -ne 'FileSystem') {
            throw 'Formatting and analysis configurations must be files.'
        }
        $configurations[$entry[0]] = $configuration.FullName
    }
}
# The platform-neutral cpp templates are layered under the MSVC ones; an MSVC
# template replaces a shared template at the same relative path.
$templateRoots = @(
    (Join-Path $PSScriptRoot '../../../base/utility/scripts/templates'),
    (Join-Path $PSScriptRoot 'templates')
)
$templates = [ordered]@{}
foreach ($templateRoot in $templateRoots) {
    if (!(Test-Path -LiteralPath $templateRoot -PathType Container)) {
        throw 'The packaged MSVC templates are missing.'
    }
    $resolvedRoot = (Resolve-Path -LiteralPath $templateRoot).Path
    foreach ($template in Get-ChildItem -LiteralPath $resolvedRoot -Recurse -Force -File -Filter '*.in') {
        $relative = [IO.Path]::GetRelativePath($resolvedRoot, $template.FullName)
        $templates[$relative.Substring(0, $relative.Length - '.in'.Length)] = $template.FullName
    }
}
if (!$templates.Count) { throw 'The packaged MSVC templates are missing.' }
if (!$PSCmdlet.ShouldProcess($projectPath, 'Create MSVC console project')) { return }

$namespace = [regex]::Replace($Name, '[^A-Za-z0-9]', '_')
$namespaceUpper = $namespace.ToUpperInvariant()

New-Item -ItemType Directory -Path $projectPath -ErrorAction Stop | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
foreach ($relative in $templates.Keys) {
    $target = Join-Path $projectPath $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    $text = [IO.File]::ReadAllText($templates[$relative])
    $text = $text.Replace('__CPP_STANDARD__', [string]$CppStandard).Replace('__NAMESPACE_UPPER__', $namespaceUpper).Replace('__NAMESPACE__', $namespace).Replace('__PROJECT__', $Name)
    [IO.File]::WriteAllText($target, $text, $utf8)
}
foreach ($configurationName in $configurations.Keys) {
    Copy-Item -LiteralPath $configurations[$configurationName] -Destination (Join-Path $projectPath $configurationName)
}
Write-Output "Created $projectPath (C++$CppStandard, MSVC x64)."
foreach ($configurationName in @('.clang-format', '.clang-tidy')) {
    $origin = if ($configurations.ContainsKey($configurationName)) { $configurations[$configurationName] } else { 'the canonical cpp configuration' }
    Write-Output "${configurationName}: copied from $origin."
}
Write-Output 'Next: open the project and run ./scripts/Build.ps1 -Test.'
