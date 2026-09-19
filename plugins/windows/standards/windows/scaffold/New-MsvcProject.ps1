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
$templateRoot = Join-Path $PSScriptRoot 'templates'
$templates = @(Get-ChildItem -LiteralPath $templateRoot -Recurse -Force -File -Filter '*.in')
if (!$templates.Count) { throw 'The packaged MSVC templates are missing.' }
if (!$PSCmdlet.ShouldProcess($projectPath, 'Create MSVC console project')) { return }

New-Item -ItemType Directory -Path $projectPath -ErrorAction Stop | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
foreach ($template in $templates) {
    $relative = [IO.Path]::GetRelativePath($templateRoot, $template.FullName)
    $relative = $relative.Substring(0, $relative.Length - '.in'.Length)
    $target = Join-Path $projectPath $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    $text = [IO.File]::ReadAllText($template.FullName)
    $text = $text.Replace('__PROJECT__', $Name).Replace('__CPP_STANDARD__', [string]$CppStandard)
    [IO.File]::WriteAllText($target, $text, $utf8)
}
foreach ($configurationName in $configurations.Keys) {
    Copy-Item -LiteralPath $configurations[$configurationName] -Destination (Join-Path $projectPath $configurationName)
}
Write-Output "Created $projectPath (C++$CppStandard, MSVC x64)."
foreach ($configurationName in @('.clang-format', '.clang-tidy')) {
    if (!$configurations.ContainsKey($configurationName)) { Write-Output "$configurationName omitted: no existing configuration supplied." }
}
Write-Output 'Next: open the project and run ./scripts/Build.ps1.'
