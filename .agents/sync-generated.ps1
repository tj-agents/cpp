#!/usr/bin/env pwsh
<#
Regenerates everything derived from `.agents/` and `standards/`, the only two places anything is
authored.

The corpus is inverted on purpose: the doc under `standards/<domain>/` is the payload and the skill is
a router. A doc is a plain markdown file, so it has two delivery modes - `@`-imported by a repo that
wants it always-on, or routed to by its skill everywhere else. Content living inside a SKILL.md can
only ever be delivered one way, which is why the bodies moved out.

Authored:
  standards/<domain>/**.md                the standards themselves
  standards/<domain>/**.ps1, **.in         bundled text scripts and templates
  .agents/skills/<name>/SKILL.md          router: front matter + the root-relative path of its doc
  .agents/hooks/*                         the write-time router hook
  .agents/plugins/marketplace.json

Generated:
  .claude/skills/<name>/SKILL.md          verbatim copy of the router, so Claude Code opened on THIS
                                          repo sees the skill. The root-relative doc path resolves
                                          because cwd is this repo.
  plugins/<p>/skills/<name>/SKILL.md      router with its doc path rewritten relative to the SKILL.md.
                                          An installed plugin is only the plugin subtree and cwd is the
                                          consuming project, so a root-relative path would dangle.
  plugins/<p>/standards/**                full copy of the tree, for that same reason.
  plugins/<p>/hooks/*                     full copy of the hook AND its hooks.json wiring, generated so
                                          the matcher cannot drift from the tool names the hook acts on.
                                          Only `base` and an explicit time-bounded compatibility alias
                                          may receive it. Multiple canonical owners would duplicate it;
                                          omitting the legacy owner would break existing installations.
  plugins/<p>/.claude-plugin/plugin.json  Claude manifest generated from the canonical Codex manifest.
  .claude-plugin/marketplace.json         Claude marketplace generated from the canonical Codex
                                          marketplace without duplicating plugin metadata.
  standards/<domain>/INDEX.md             the tree answers "where is it"; this answers "did I document
                                          this" without opening anything.

Refuses to generate when the two structures disagree: a router naming a doc that does not exist, a doc
no router points at, or two routers claiming one doc. A tree and a skill namespace that can drift is
exactly how 754 lines of frontend law ended up with zero inbound links.

  pwsh .agents/sync-generated.ps1
  pwsh .agents/sync-generated.ps1 -Check   # verify only; non-zero exit if anything is stale
#>

[CmdletBinding()]
param([switch]$Check)

$ErrorActionPreference = 'Stop'

$repoRoot     = Split-Path -Parent $PSScriptRoot
$canonical    = Join-Path $repoRoot '.agents/skills'
$hookSource   = Join-Path $repoRoot '.agents/hooks'
$manifest     = Join-Path $repoRoot '.agents/plugins/marketplace.json'
$standardsDir = Join-Path $repoRoot 'standards'
$utf8NoBom    = New-Object System.Text.UTF8Encoding($false)

$INDEX_NAME = 'INDEX.md'

function Read-Lf([string]$path) {
    return ([System.IO.File]::ReadAllText($path) -replace "`r`n", "`n")
}

function ConvertTo-LfJson($value) {
    $json = $value | ConvertTo-Json -Depth 10 -Compress
    $json = $json.Replace('&', '\u0026').Replace("'", '\u0027').Replace('<', '\u003c').Replace('>', '\u003e')
    return ($json + "`n")
}

# Kept to string trimming rather than [Path]::GetRelativePath / Resolve-Path -RelativeBasePath: both
# need PowerShell 7, and this repo is cloned onto machines that only have 5.1.
function To-RepoRelative([string]$fullPath, [string]$base) {
    $separator = [System.IO.Path]::DirectorySeparatorChar
    $normalizedBase = ((Resolve-Path -LiteralPath $base).ProviderPath.TrimEnd('\', '/')) + $separator
    $full = (Resolve-Path -LiteralPath $fullPath).ProviderPath
    if (-not $full.StartsWith($normalizedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$full is not under $normalizedBase."
    }
    return ($full.Substring($normalizedBase.Length) -replace '\\', '/')
}

function Get-FrontMatterField([string]$text, [string]$field, [string]$name) {
    $match = [regex]::Match($text, "(?s)\A---\n.*?^${field}:[ \t]*(.+?)\n(?:[a-zA-Z-]+:|---)", 'Multiline')
    if (-not $match.Success) {
        throw "$name/SKILL.md has no parsable ``${field}:`` in its front matter."
    }
    $value = $match.Groups[1].Value.Trim() -replace "\s*\n\s*", " "
    # A bare colon-space anywhere in an unquoted YAML scalar silently truncates the value, and the
    # description is what decides whether the skill loads at all - a truncated one never fires.
    if ($field -eq 'description' -and $value -match ':\s') {
        throw "$name/SKILL.md description contains a colon-space, which breaks the YAML scalar: $value"
    }
    return $value
}

# The router's single authored fact about its payload: the root-relative path of its doc, in backticks.
# Parsed rather than held in a side table, because a second structure is a second thing that drifts.
function Get-RoutedDoc([string]$text, [string]$name) {
    $found = [regex]::Matches($text, '`(standards/[^`]+\.md)`')
    $paths = @($found | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    if ($paths.Count -eq 0) {
        throw "$name/SKILL.md names no ``standards/...md`` doc, so it routes nowhere."
    }
    if ($paths.Count -gt 1) {
        throw "$name/SKILL.md names $($paths.Count) docs ($($paths -join ', ')); a router owns exactly one."
    }
    return $paths[0]
}

# The plugin copy must name only what ships beside it. The authored router also cites the deployed
# ~/.agents/standards path, which need not exist on a machine that installed the plugin and never cloned
# the repo - a reader who tries it first finds nothing.
function Rewrite-ForPlugin([string]$body) {
    $rewritten = [regex]::Replace(
        $body,
        'The standard is `standards/(?<doc>[^`]+)` in `[^`]+`, deployed to `~/\.agents/standards/[^`]+`\.',
        'The standard is `../../standards/${doc}`, shipped in this plugin.')
    if ($rewritten -eq $body) {
        throw "plugin rewrite matched nothing; the router sentence changed shape and the copy would keep a path that dangles on install."
    }
    return $rewritten
}

# Skills stay flat: discovery is <root>/skills/*/SKILL.md and does not recurse. Only content nests.
$skillDirs = @(Get-ChildItem -Path $canonical -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | Sort-Object Name)
if (-not $skillDirs) { throw "No canonical skills found under .agents/skills." }

$routers = [ordered]@{}
foreach ($dir in $skillDirs) {
    $text = Read-Lf (Join-Path $dir.FullName 'SKILL.md')
    $routers[$dir.Name] = [pscustomobject]@{
        Name        = $dir.Name
        Body        = $text
        Description = Get-FrontMatterField $text 'description' $dir.Name
        Doc         = Get-RoutedDoc $text $dir.Name
    }
}

# The standards tree is walked recursively - nesting is the whole point of the tree.
$docs = @()
if (Test-Path $standardsDir) {
    $docs = @(Get-ChildItem -Path $standardsDir -Recurse -File -Filter '*.md' |
        Where-Object { $_.Name -ne $INDEX_NAME } |
        ForEach-Object { To-RepoRelative $_.FullName $repoRoot } |
        Sort-Object)
}
if (-not $docs) { throw "No standards docs found under standards/." }

# Bundled text scripts/templates travel with their owning standards domain.
$resources = @(Get-ChildItem -LiteralPath $standardsDir -Recurse -Force -File |
    Where-Object { $_.Extension -ne '.md' } |
    ForEach-Object {
        if ($_.Extension -notin '.ps1', '.in') { throw "Unsupported standards resource: $($_.FullName)" }
        To-RepoRelative $_.FullName $repoRoot
    })

# Neither structure may grow an orphan.
$problems = @()
foreach ($router in $routers.Values) {
    if ($docs -notcontains $router.Doc) {
        $problems += "skill '$($router.Name)' routes to '$($router.Doc)', which does not exist."
    }
}
foreach ($doc in $docs) {
    $owners = @($routers.Values | Where-Object { $_.Doc -eq $doc } | Select-Object -ExpandProperty Name)
    if ($owners.Count -eq 0) {
        $problems += "doc '$doc' has no routing skill, so nothing loads it."
    }
    if ($owners.Count -gt 1) {
        $problems += "doc '$doc' is routed by $($owners.Count) skills ($($owners -join ', ')); it needs exactly one owner."
    }
}
if ($problems) {
    Write-Host "The standards tree and the skill namespace disagree:"
    foreach ($problem in $problems) { Write-Host "  $problem" }
    exit 1
}

$pluginRoot = Join-Path $repoRoot 'plugins'
$plugins = @()
if (Test-Path $pluginRoot) { $plugins = @(Get-ChildItem -Path $pluginRoot -Directory | Sort-Object Name) }

# Refuse to generate against a marketplace that points at a plugin that is not there, or a plugin
# with no manifest of its own - an unroutable package installs and delivers nothing.
if (-not (Test-Path $manifest)) { throw "Missing canonical manifest .agents/plugins/marketplace.json." }
$manifestBody = Read-Lf $manifest
$manifestJson = ConvertFrom-Json $manifestBody
$declared = @()
foreach ($entry in $manifestJson.plugins) {
    $declared += $entry.name
    if (-not $entry.source.path) {
        throw "marketplace.json entry '$($entry.name)' has no Codex local source path."
    }
    $source = Join-Path $repoRoot ($entry.source.path -replace '^\./', '')
    if (-not (Test-Path $source)) {
        throw "marketplace.json declares '$($entry.name)' at $($entry.source.path), which does not exist."
    }
    if (-not (Test-Path (Join-Path $source '.codex-plugin/plugin.json'))) {
        throw "Plugin '$($entry.name)' has no canonical .codex-plugin/plugin.json."
    }
    $pluginManifest = ConvertFrom-Json (Read-Lf (Join-Path $source '.codex-plugin/plugin.json'))
    if ($pluginManifest.name -ne $entry.name) {
        throw "Marketplace entry '$($entry.name)' points at a manifest named '$($pluginManifest.name)'."
    }
}

function Rewrite-CompatibilityIdentifiers([string]$body, [string]$pluginName) {
    if (-not $compatibilityAliases.ContainsKey($pluginName)) { return $body }
    $alias = $compatibilityAliases[$pluginName]
    foreach ($property in $alias.qualifiedSkillAliases.PSObject.Properties) {
        $body = $body.Replace($property.Name, $property.Value)
    }
    foreach ($property in $alias.identifierAliases.PSObject.Properties) {
        $body = $body.Replace("$($property.Name):", "$($property.Value):")
    }
    foreach ($property in $alias.selectorAliases.PSObject.Properties) {
        $body = $body.Replace($property.Name, $property.Value)
    }
    return $body
}

# Which plugin ships which domains. A consumer installs per stack, so the split is authored rather
# than inferred from a plugin's name - and cross-checked both ways against the marketplace so the two
# cannot drift into disagreeing about what exists.
$payloadsFile = Join-Path $repoRoot '.agents/plugins/payloads.json'
if (-not (Test-Path $payloadsFile)) { throw "Missing .agents/plugins/payloads.json." }
$payloadsJson = ConvertFrom-Json (Read-Lf $payloadsFile)
$payloads = $payloadsJson.payloads
$publicPlugins = @($payloadsJson.publicPlugins)
if (-not $publicPlugins -or (($manifestJson.plugins | Select-Object -First $publicPlugins.Count).name -join ',') -ne ($publicPlugins -join ',')) {
    throw "marketplace.json must list payloads.json publicPlugins first and in the same order."
}
$pluginDomains = @{}
foreach ($property in $payloads.PSObject.Properties) {
    if ($declared -notcontains $property.Name) {
        throw "payloads.json declares plugin '$($property.Name)', which marketplace.json does not."
    }
    $pluginDomains[$property.Name] = @($property.Value)
}
foreach ($name in $declared) {
    if (-not $pluginDomains.ContainsKey($name)) {
        throw "marketplace.json declares plugin '$name', which payloads.json assigns no domains."
    }
}
foreach ($plugin in $plugins) {
    if (-not $pluginDomains.ContainsKey($plugin.Name)) {
        throw "plugins/$($plugin.Name) exists but is declared nowhere; add it to marketplace.json and payloads.json."
    }
    foreach ($domain in $pluginDomains[$plugin.Name]) {
        if (-not (Test-Path (Join-Path $standardsDir $domain))) {
            throw "plugin '$($plugin.Name)' claims domain '$domain', which is not in standards/."
        }
    }
}
$unshipped = @($docs | ForEach-Object { ($_ -split '/')[1] } | Sort-Object -Unique |
    Where-Object { $domain = $_; -not (@($pluginDomains.Values | ForEach-Object { $_ }) -contains $domain) })
if ($unshipped) {
    throw "standards domain(s) '$($unshipped -join ', ')' are in no plugin, so a clone cannot install them."
}

# Dependencies are an explicit repository contract because neither supported marketplace manifest has a
# portable dependency field. Validate existence and cycles here so a platform layer cannot silently ship
# without its base.
$dependencies = @{}
if ($payloadsJson.dependencies) {
    foreach ($property in $payloadsJson.dependencies.PSObject.Properties) {
        if ($declared -notcontains $property.Name) { throw "dependencies names missing plugin '$($property.Name)'." }
        $dependencies[$property.Name] = @($property.Value)
        foreach ($dependency in $dependencies[$property.Name]) {
            if ($declared -notcontains $dependency) { throw "plugin '$($property.Name)' depends on missing plugin '$dependency'." }
            if ($dependency -eq $property.Name) { throw "plugin '$($property.Name)' depends on itself." }
        }
    }
}
function Assert-AcyclicDependency([string]$name, [hashtable]$active, [hashtable]$complete) {
    if ($active.ContainsKey($name)) { throw "Plugin dependency cycle includes '$name'." }
    if ($complete.ContainsKey($name)) { return }
    $active[$name] = $true
    if ($dependencies.ContainsKey($name)) {
        foreach ($dependency in @($dependencies[$name])) { Assert-AcyclicDependency $dependency $active $complete }
    }
    $active.Remove($name)
    $complete[$name] = $true
}
$completeDependencies = @{}
foreach ($name in $declared) { Assert-AcyclicDependency $name @{} $completeDependencies }

$compatibilityAliases = @{}
if ($payloadsJson.compatibilityAliases) {
    foreach ($property in $payloadsJson.compatibilityAliases.PSObject.Properties) {
        if ($declared -notcontains $property.Name) { throw "compatibility alias '$($property.Name)' is missing from marketplace.json." }
        if ($publicPlugins -contains $property.Name) { throw "compatibility alias '$($property.Name)' cannot be a public plugin." }
        if ($publicPlugins -notcontains $property.Value.replacedBy) { throw "compatibility alias '$($property.Name)' has unknown replacement '$($property.Value.replacedBy)'." }
        try { $removeAfter = [datetime]::ParseExact($property.Value.removeAfter, 'yyyy-MM-dd', $null) }
        catch { throw "compatibility alias '$($property.Name)' needs a yyyy-MM-dd removeAfter date." }
        if ($removeAfter.Date -lt [datetime]::Today) {
            throw "compatibility alias '$($property.Name)' expired on $($property.Value.removeAfter); remove it before generating a release."
        }
        $compatibilityAliases[$property.Name] = $property.Value
    }
}

# The canonical base and its temporary compatibility alias both need standalone detection. Installing
# both briefly during migration duplicates only the same idempotent session context; the alias disappears
# at its declared removal date.
$hookOwners = @($payloadsJson.hooks)
$hookFiles = @()
if (Test-Path $hookSource) {
    $hookFiles = @(Get-ChildItem -Path $hookSource -File | Where-Object { $_.Extension -in '.py', '.json' })
}
if ($hookFiles.Count -and -not $hookOwners) {
    throw ".agents/hooks holds $($hookFiles.Count) file(s) but payloads.json names no 'hooks' owner, so every plugin would ship a duplicate copy."
}
foreach ($hookOwner in $hookOwners) {
    if ($declared -notcontains $hookOwner) {
        throw "payloads.json assigns the hooks to '$hookOwner', which marketplace.json does not declare."
    }
    if ($hookOwner -ne 'base' -and -not $compatibilityAliases.ContainsKey($hookOwner)) {
        throw "Only base or a declared compatibility alias may ship the C++ detection hook; found '$hookOwner'."
    }
}

# relative path -> LF-normalized content
$generated = [ordered]@{}

foreach ($router in $routers.Values) {
    $generated[".claude/skills/$($router.Name)/SKILL.md"] = $router.Body
}

foreach ($plugin in $plugins) {
    $codexPluginManifest = Join-Path $plugin.FullName '.codex-plugin/plugin.json'
    $codexPluginJson = ConvertFrom-Json (Read-Lf $codexPluginManifest)
    $claudePluginJson = [ordered]@{
        name        = $codexPluginJson.name
        version     = $codexPluginJson.version
        description = $codexPluginJson.description
        author      = $codexPluginJson.author
        repository  = $codexPluginJson.repository
        keywords    = @($codexPluginJson.keywords)
        skills      = $codexPluginJson.skills
    }
    $generated["plugins/$($plugin.Name)/.claude-plugin/plugin.json"] = ConvertTo-LfJson $claudePluginJson

    # A plugin ships only the domains it claims, and only the routers for those domains - a TypeScript
    # project installing a React plugin must not also receive the .NET corpus.
    $mine = @($docs | Where-Object {
        $pluginDomains[$plugin.Name] -contains (($_ -split '/')[1])
    })
    foreach ($doc in $mine) {
        $docBody = Rewrite-CompatibilityIdentifiers (Read-Lf (Join-Path $repoRoot $doc)) $plugin.Name
        $generated["plugins/$($plugin.Name)/$doc"] = $docBody
        $owner = @($routers.Values | Where-Object { $_.Doc -eq $doc })[0]
        $skillName = $owner.Name
        $skillBody = Rewrite-ForPlugin $owner.Body
        if ($compatibilityAliases.ContainsKey($plugin.Name) -and $compatibilityAliases[$plugin.Name].skillAliases) {
            $aliasProperty = $compatibilityAliases[$plugin.Name].skillAliases.PSObject.Properties[$owner.Name]
            if ($aliasProperty) {
                $skillName = $aliasProperty.Value
                $skillBody = [regex]::Replace($skillBody, "(?m)^name: $([regex]::Escape($owner.Name))$", "name: $skillName")
            }
        }
        $skillBody = Rewrite-CompatibilityIdentifiers $skillBody $plugin.Name
        # skills/<name>/SKILL.md -> the plugin's own copy of the tree, two levels up.
        $generated["plugins/$($plugin.Name)/skills/$skillName/SKILL.md"] = $skillBody
    }
    foreach ($resource in $resources) {
        if ($pluginDomains[$plugin.Name] -contains (($resource -split '/')[1])) {
            $generated["plugins/$($plugin.Name)/$resource"] = Read-Lf (Join-Path $repoRoot $resource)
        }
    }
    if ($hookOwners -contains $plugin.Name) {
        foreach ($hook in $hookFiles) {
            $hookBody = Read-Lf $hook.FullName
            $hookBody = Rewrite-CompatibilityIdentifiers $hookBody $plugin.Name
            $generated["plugins/$($plugin.Name)/hooks/$($hook.Name)"] = $hookBody
        }
    }
}

$claudePlugins = @($manifestJson.plugins | ForEach-Object {
    [ordered]@{
        name   = $_.name
        source = $_.source.path
    }
})
$claudeMarketplace = [ordered]@{
    name        = $manifestJson.name
    description = $payloadsJson.description
    owner       = [ordered]@{ name = (ConvertFrom-Json (Read-Lf (Join-Path $plugins[0].FullName '.codex-plugin/plugin.json'))).author.name }
    plugins     = $claudePlugins
}
$generated['.claude-plugin/marketplace.json'] = ConvertTo-LfJson $claudeMarketplace

# One index per domain, generated from the tree so it cannot drift from it.
$domains = @($docs | ForEach-Object { ($_ -split '/')[1] } | Sort-Object -Unique)
foreach ($domain in $domains) {
    $rows = @()
    # Domain-root docs first, then each subfolder as a block. A plain path sort interleaves them.
    # Sorted ORDINALLY, not with Sort-Object: its comparison is culture-aware, and cultures disagree
    # about punctuation. `COMMIT.md` vs `COMMIT_ALL.md` ('.' against '_') ordered one way on Windows and
    # the other under Linux ICU, so the generated INDEX differed by platform and CI called a locally
    # current tree stale. A generated file that depends on the generating machine's culture is not
    # generated. Folder and path are packed into one key with a tab, which no path contains.
    $keyed = [System.Collections.Generic.List[string]]::new()
    foreach ($doc in @($docs | Where-Object { $_ -like "standards/$domain/*" })) {
        $withinDomain = $doc -replace "^standards/$domain/", ''
        $folder = if ($withinDomain -match '/') { $withinDomain.Substring(0, $withinDomain.LastIndexOf('/')) } else { '' }
        $keyed.Add("$folder`t$doc")
    }
    $keyed.Sort([System.StringComparer]::Ordinal)
    $inDomain = @($keyed | ForEach-Object { ($_ -split "`t", 2)[1] })
    foreach ($doc in $inDomain) {
        $owner = @($routers.Values | Where-Object { $_.Doc -eq $doc })[0]
        $heading = @((Read-Lf (Join-Path $repoRoot $doc)) -split "`n" |
            Where-Object { $_ -match '^#\s+' } | Select-Object -First 1)
        $title = ($heading[0] -replace '^#\s+', '')
        $relative = ($doc -replace "^standards/$domain/", '')
        $rows += "| [``$relative``]($relative) | $title | ``$($owner.Name)`` |"
    }
    $lines = @(
        "# $domain standards",
        '',
        'Generated by `.agents/sync-generated.ps1` from the tree. Do not edit.',
        '',
        '| Doc | Covers | Skill |',
        '|---|---|---|'
    ) + $rows + @('')
    $generated["standards/$domain/$INDEX_NAME"] = ($lines -join "`n")
}

$stale = @(); $written = @(); $unchanged = @()

foreach ($relative in $generated.Keys) {
    $target  = Join-Path $repoRoot $relative
    $body    = $generated[$relative]
    $current = $null
    if (Test-Path $target) { $current = Read-Lf $target }
    if ($current -eq $body) { $unchanged += $relative; continue }
    $stale += $relative
    if ($Check) { continue }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    [System.IO.File]::WriteAllText($target, ($body -replace "`n", "`r`n"), $utf8NoBom)
    $written += $relative
}

# Prune every generated artefact this run did not just author. Membership of $generated is the test, not
# "is there still a skill by this name" - a doc moving between plugins leaves a stale copy behind that a
# name check would happily keep, and a consumer would then install two conflicting copies of one rule.
$pruned = @()
$generatedRoots = @(Join-Path $repoRoot '.claude/skills')
foreach ($plugin in $plugins) {
    $generatedRoots += (Join-Path $plugin.FullName 'skills')
    $generatedRoots += (Join-Path $plugin.FullName 'standards')
    $generatedRoots += (Join-Path $plugin.FullName 'hooks')
    $generatedRoots += (Join-Path $plugin.FullName '.claude-plugin')
}
foreach ($root in $generatedRoots) {
    if (-not (Test-Path $root)) { continue }
    foreach ($file in Get-ChildItem -Path $root -Recurse -File) {
        $relative = To-RepoRelative $file.FullName $repoRoot
        if ($generated.Contains($relative)) { continue }
        $pruned += $relative
        if (-not $Check) { Remove-Item -Force $file.FullName }
    }
}
if (-not $Check) {
    foreach ($root in $generatedRoots) {
        if (-not (Test-Path $root)) { continue }
        Get-ChildItem -Path $root -Recurse -Directory |
            Sort-Object { $_.FullName.Length } -Descending |
            Where-Object { -not (Get-ChildItem -Path $_.FullName -Recurse -File) } |
            ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
    }
}

if ($Check) {
    if ($stale.Count -or $pruned.Count) {
        Write-Host "STALE: $($stale.Count) generated file(s), $($pruned.Count) orphan(s). Run: pwsh .agents/sync-generated.ps1"
        foreach ($item in ($stale + $pruned)) { Write-Host "  $item" }
        exit 1
    }
    Write-Host "generated files are current: $($unchanged.Count) checked ($($routers.Count) skills, $($docs.Count) docs)"
    exit 0
}

Write-Host "generated: $($generated.Count) file(s) from $($routers.Count) skills and $($docs.Count) docs | $($written.Count) written | $($unchanged.Count) unchanged | $($pruned.Count) pruned"
foreach ($item in $written) { Write-Host "  written: $item" }
foreach ($item in $pruned)  { Write-Host "  pruned:  $item" }
