#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$Project
)

$ErrorActionPreference = 'Stop'
$root = Get-Item -LiteralPath $Project -ErrorAction Stop
if (!$root.PSIsContainer -or $root.PSProvider.Name -ne 'FileSystem') {
    throw 'Project must be an existing filesystem directory.'
}
$root = $root.FullName

$sharedRoot = Join-Path $PSScriptRoot '../../../base/utility/scripts/templates'
$templateRoot = Join-Path $PSScriptRoot 'templates'
foreach ($required in @($sharedRoot, $templateRoot)) {
    if (!(Test-Path -LiteralPath $required -PathType Container)) { throw 'The packaged Win32 templates are missing.' }
}

function Read-Normalized([string]$Path) {
    [IO.File]::ReadAllText($Path).Replace("`r`n", "`n")
}

$rootCMake = Join-Path $root 'CMakeLists.txt'
if (!(Test-Path -LiteralPath $rootCMake -PathType Leaf)) { throw "Not a scaffolded CMake project: $root" }
$match = [regex]::Match((Read-Normalized $rootCMake), '(?m)^project\(\s*([A-Za-z][A-Za-z0-9_-]*)')
if (!$match.Success) { throw 'The root CMakeLists.txt does not declare project(<name>).' }
$name = $match.Groups[1].Value
$namespace = [regex]::Replace($name, '[^A-Za-z0-9]', '_')
$namespaceUpper = $namespace.ToUpperInvariant()

function Expand-Template([string]$Path) {
    (Read-Normalized $Path).Replace('__NAMESPACE_UPPER__', $namespaceUpper).Replace('__NAMESPACE__', $namespace).Replace('__PROJECT__', $name)
}

# Only a fresh scaffold is converted: never overwrite application code or build rules.
foreach ($relative in @('app/CMakeLists.txt', 'app/src/main.cpp')) {
    $existing = Join-Path $root $relative
    if (!(Test-Path -LiteralPath $existing -PathType Leaf) -or (Read-Normalized $existing) -ne (Expand-Template (Join-Path $sharedRoot "$relative.in"))) {
        throw "$relative is not the unmodified scaffold output; apply the Win32 application settings by hand."
    }
}
foreach ($relative in @('app/app.manifest', 'app/app.rc')) {
    if (Test-Path -LiteralPath (Join-Path $root $relative)) { throw "$relative already exists." }
}

$utf8 = [Text.UTF8Encoding]::new($false)
$writes = [ordered]@{}
foreach ($template in Get-ChildItem -LiteralPath $templateRoot -Recurse -File -Filter '*.in') {
    $relative = [IO.Path]::GetRelativePath($templateRoot, $template.FullName)
    $writes[$relative.Substring(0, $relative.Length - '.in'.Length)] = Expand-Template $template.FullName
}
$manual = [Collections.Generic.List[string]]::new()

# Win32 idioms that the canonical analysis set would otherwise flag.
$tidyPath = Join-Path $root '.clang-tidy'
if ((Test-Path -LiteralPath $tidyPath) -and (Read-Normalized $tidyPath) -eq (Expand-Template (Join-Path $sharedRoot '.clang-tidy.in'))) {
    $tidy = Read-Normalized $tidyPath
    $header = @(
        '# Win32 carve-outs on top of the canonical check set:',
        '#  - reinterpret-cast / int-to-ptr: inherent to Win32 (HWND <-> object through',
        '#    GWLP_USERDATA and CREATESTRUCT, the (HBRUSH)(COLOR_x + 1) idiom).',
        '#  - convert-member-functions-to-static: message hooks are instance methods by contract.',
        '#  - named-parameter: unused callback and entry-point parameters stay unnamed; naming',
        '#    them triggers the compiler''s own unreferenced-parameter warning.'
    ) -join "`n"
    $checks = @(
        '  -cppcoreguidelines-pro-type-reinterpret-cast,',
        '  -performance-no-int-to-ptr,',
        '  -readability-convert-member-functions-to-static,',
        '  -readability-named-parameter'
    ) -join "`n"
    $tidy = $tidy.Replace("  -portability-avoid-pragma-once`nWarningsAsErrors:", "  -portability-avoid-pragma-once,`n$checks`nWarningsAsErrors:")
    $writes['.clang-tidy'] = "$header`n$tidy"
} else {
    $manual.Add('.clang-tidy: not the canonical configuration; add the Win32 carve-outs by hand.')
}

# <windows.h> must precede every other Windows header, so pin it to the first include block.
$formatPath = Join-Path $root '.clang-format'
if ((Test-Path -LiteralPath $formatPath) -and (Read-Normalized $formatPath) -eq (Expand-Template (Join-Path $sharedRoot '.clang-format.in'))) {
    $categories = @(
        'IncludeCategories:',
        "  - Regex: '^<windows\.h>$'",
        '    Priority: 1',
        "  - Regex: '^<ext/.*\.h>'",
        '    Priority: 3',
        "  - Regex: '^<.*\.h>'",
        '    Priority: 2',
        "  - Regex: '^<.*'",
        '    Priority: 3',
        "  - Regex: '.*'",
        '    Priority: 4'
    ) -join "`n"
    $format = (Read-Normalized $formatPath).TrimEnd("`n")
    if ($format.EndsWith("`n...")) { $format = $format.Substring(0, $format.Length - 4) }
    $writes['.clang-format'] = "$format`n$categories`n...`n"
} else {
    $manual.Add('.clang-format: not the canonical configuration; pin <windows.h> first with IncludeCategories by hand.')
}

$agentsPath = Join-Path $root 'AGENTS.md'
if (Test-Path -LiteralPath $agentsPath) {
    $writes['AGENTS.md'] = (Read-Normalized $agentsPath).TrimEnd("`n") + "`n`nThe ``app`` target is a user-mode Win32 GUI application.`n"
}
$readmePath = Join-Path $root 'README.md'
if (Test-Path -LiteralPath $readmePath) {
    $writes['README.md'] = (Read-Normalized $readmePath).TrimEnd("`n") + "`n`n" + (@(
        '## Win32',
        '',
        'The `app` target is a Unicode Win32 GUI application: `wWinMain`, no console window,',
        'and `app.manifest` (Per-Monitor V2 DPI awareness, Common Controls v6, UTF-8 active code',
        'page, `asInvoker`) embedded through `app.rc`. Keep window procedures and message',
        'handling thin; put testable logic in `libs/`.'
    ) -join "`n") + "`n"
}

# Replace the route profile with the matching toolchain + Win32 profile when one is packaged.
$routesPath = Join-Path $root '.agents/skill-routes.json'
if (Test-Path -LiteralPath $routesPath) {
    $toolchain = (Get-Content -LiteralPath $routesPath -Raw | ConvertFrom-Json).profile.toolchain
    $profilePath = if ($toolchain) { Join-Path $PSScriptRoot "routes/$toolchain.json" } else { $null }
    if ($profilePath -and (Test-Path -LiteralPath $profilePath -PathType Leaf)) {
        $writes['.agents/skill-routes.json'] = Read-Normalized $profilePath
    } else {
        $manual.Add('.agents/skill-routes.json: regenerate the route profile with the Win32 API selected.')
    }
}

if (!$PSCmdlet.ShouldProcess($root, 'Convert the app target to a Win32 GUI application')) { return }
foreach ($relative in $writes.Keys) {
    $target = Join-Path $root $relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    [IO.File]::WriteAllText($target, $writes[$relative], $utf8)
}
Write-Output "Converted $name to a Win32 GUI application."
foreach ($note in $manual) { Write-Output "Manual step: $note" }
