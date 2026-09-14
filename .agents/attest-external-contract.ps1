param(
    [Parameter(Mandatory = $true)]
    [string] $ConsumerSource,

    [Parameter(Mandatory = $true)]
    [string] $CandidateSha,

    [Parameter(Mandatory = $true)]
    [string] $AgentStandardsSource
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$consumerRepository = "tomjseery/cpp-agents"
$producerRepository = "Concertable/agent-standards"
$producerUrl = "https://github.com/$producerRepository"
$expectedProducerCommit = "93d8bd57fbfbd793acdebe542f7ae270a0c1d2a1"
$expectedVersion = "0.1.6"
$expectedManifest = "plugins/concertable/.codex-plugin/plugin.json"
$expectedSkillsRoot = "plugins/concertable/codex-skills"
$expectedSkills = @("docs-and-debt", "skill-routes")
$attesterLogin = "tomjseery"
$attesterId = 183629855
$statusContext = "agent-standards/provenance"
$contractPath = ".agents/plugins/skill-contract.json"
$evidenceRoot = "contracts/concertable-0.1.6"
$expectedCandidateObjects = [ordered]@{
    ".agents/plugins/skill-contract.json" = "cd5c16c7bffd9e48f21a42ada33ff03528288bfb"
    ".agents/tests/test_attester_safety.py" = "eb279a45b18d60888fe765c5fc8cf4b0d2251fbd"
    ".agents/tests/test_marketplace_contract.py" = "004c73dc421ed64a71563140b62b4f624f5bec7e"
    ".github/workflows/attester-safety.yml" = "42652f96cef2be751872cc376719b26d76dc3494"
    ".github/workflows/ci.yml" = "0e15c93383f209a28dde4b034b5a7754ac74c560"
    "contracts" = "158049858856c30eb91a37704512d9dcda4283c2"
}

function Invoke-CheckedGit {
    param(
        [Parameter(Mandatory = $true)][string] $Repository,
        [Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments
    )
    $output = & $gitExecutable --no-replace-objects -C $Repository @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed in ${Repository}: git $($Arguments -join ' ')"
    }
    return $output
}

function Invoke-CheckedGh {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments)
    $output = & $ghExecutable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI failed: gh $($Arguments -join ' ')"
    }
    return $output
}

function Get-GitBlobBytes {
    param(
        [Parameter(Mandatory = $true)][string] $Repository,
        [Parameter(Mandatory = $true)][string] $ObjectSpec
    )
    $start = [System.Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $gitExecutable
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.ArgumentList.Add("--no-replace-objects")
    $start.ArgumentList.Add("-C")
    $start.ArgumentList.Add($Repository)
    $start.ArgumentList.Add("cat-file")
    $start.ArgumentList.Add("blob")
    $start.ArgumentList.Add($ObjectSpec)
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $start
    if (-not $process.Start()) {
        throw "Unable to start Git."
    }
    $buffer = [System.IO.MemoryStream]::new()
    try {
        $process.StandardOutput.BaseStream.CopyTo($buffer)
        $errorText = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($process.ExitCode -ne 0) {
            throw "git cat-file failed for ${ObjectSpec}: $errorText"
        }
        return ,$buffer.ToArray()
    }
    finally {
        $buffer.Dispose()
        $process.Dispose()
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][byte[]] $Bytes)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}

function ConvertFrom-Utf8Json {
    param([Parameter(Mandatory = $true)][byte[]] $Bytes)
    return [Text.Encoding]::UTF8.GetString($Bytes) | ConvertFrom-Json
}

function Assert-ExactString {
    param(
        [AllowNull()][object] $Value,
        [Parameter(Mandatory = $true)][string] $Expected,
        [Parameter(Mandatory = $true)][string] $Name
    )
    if ($Value -isnot [string] -or $Value -cne $Expected) {
        throw "$Name does not match the trusted string value."
    }
}

function Assert-CanonicalRemote {
    param(
        [Parameter(Mandatory = $true)][string] $Repository,
        [Parameter(Mandatory = $true)][string] $ExpectedSlug
    )
    $origin = (Invoke-CheckedGit -Repository $Repository remote get-url origin).Trim()
    if ($origin -notmatch '^(?:https://github\.com/|git@github\.com:)(?<slug>[^/]+/[^/]+?)(?:\.git)?$' -or
        $Matches.slug -ine $ExpectedSlug) {
        throw "Unexpected origin for ${Repository}: $origin"
    }
}

function Test-PathWithin {
    param(
        [Parameter(Mandatory = $true)][string] $Path,
        [Parameter(Mandatory = $true)][string] $Root
    )
    $relative = [IO.Path]::GetRelativePath($Root, $Path)
    return -not [IO.Path]::IsPathRooted($relative) -and
        $relative -ne ".." -and
        -not $relative.StartsWith("..$([IO.Path]::DirectorySeparatorChar)", [StringComparison]::Ordinal)
}

$trustedRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$consumerRoot = (Resolve-Path -LiteralPath $ConsumerSource).Path
$producerRoot = (Resolve-Path -LiteralPath $AgentStandardsSource).Path
Set-Location -LiteralPath $trustedRoot

$gitExecutable = (Get-Command git -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$ghExecutable = (Get-Command gh -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$gitExecutable = (Resolve-Path -LiteralPath $gitExecutable).Path
$ghExecutable = (Resolve-Path -LiteralPath $ghExecutable).Path
foreach ($executable in @($gitExecutable, $ghExecutable)) {
    if (Test-PathWithin -Path $executable -Root $consumerRoot) {
        throw "Refusing candidate-owned executable: $executable"
    }
}

if ($CandidateSha -notmatch "^[0-9a-f]{40}$") {
    throw "CandidateSha must be a full lowercase Git commit SHA."
}

$trustedHead = (Invoke-CheckedGit -Repository $trustedRoot rev-parse HEAD).Trim()
$remoteMain = (Invoke-CheckedGh api "repos/$consumerRepository/git/ref/heads/main" --jq ".object.sha").Trim()
if ($trustedHead -ne $remoteMain) {
    throw "Run the attester from an exact checkout of the canonical main branch."
}
& $gitExecutable --no-replace-objects -C $trustedRoot diff --quiet HEAD -- .agents/attest-external-contract.ps1
if ($LASTEXITCODE -ne 0) {
    throw "The trusted attester differs from canonical main."
}

Assert-CanonicalRemote -Repository $consumerRoot -ExpectedSlug $consumerRepository
Assert-CanonicalRemote -Repository $producerRoot -ExpectedSlug $producerRepository

$remoteCandidate = (Invoke-CheckedGh api "repos/$consumerRepository/commits/$CandidateSha" --jq ".sha").Trim()
if ($remoteCandidate -ne $CandidateSha) {
    throw "The candidate is not present in the canonical consumer repository."
}

$trustedAttesterBlob = (Invoke-CheckedGit -Repository $trustedRoot rev-parse "${trustedHead}:.agents/attest-external-contract.ps1").Trim()
$trustedGateBlob = (Invoke-CheckedGit -Repository $trustedRoot rev-parse "${trustedHead}:.github/workflows/provenance-gate.yml").Trim()
$candidateAttesterBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:.agents/attest-external-contract.ps1").Trim()
$candidateGateBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:.github/workflows/provenance-gate.yml").Trim()
if ($candidateAttesterBlob -ne $trustedAttesterBlob -or $candidateGateBlob -ne $trustedGateBlob) {
    throw "The candidate trust tools do not match canonical main."
}
foreach ($entry in $expectedCandidateObjects.GetEnumerator()) {
    $actual = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:$($entry.Key)").Trim()
    if ($actual -ne $entry.Value) {
        throw "The candidate object $($entry.Key) does not match the separately reviewed object."
    }
}

$producerHead = (Invoke-CheckedGit -Repository $producerRoot rev-parse HEAD).Trim()
if ($producerHead -ne $expectedProducerCommit) {
    throw "The producer checkout is not at the trusted commit."
}
$producerComparison = Invoke-CheckedGh api "repos/$producerRepository/compare/${expectedProducerCommit}...main" | Out-String | ConvertFrom-Json
if ($producerComparison.base_commit.sha -ne $expectedProducerCommit -or
    $producerComparison.merge_base_commit.sha -ne $expectedProducerCommit -or
    $producerComparison.status -notin @("ahead", "identical")) {
    throw "The trusted producer commit is not reachable from authenticated canonical main."
}
$producerRecord = Invoke-CheckedGh api "repos/$producerRepository/commits/$expectedProducerCommit" | Out-String | ConvertFrom-Json
if ($producerRecord.sha -ne $expectedProducerCommit -or -not $producerRecord.commit.verification.verified) {
    throw "The producer commit is absent from the canonical repository or is not verified."
}

$contract = ConvertFrom-Utf8Json (Get-GitBlobBytes -Repository $consumerRoot -ObjectSpec "${CandidateSha}:$contractPath")
$external = $contract.externalPlugins.concertable
Assert-ExactString $external.repository $producerUrl "contract repository"
Assert-ExactString $external.sourceCommit $expectedProducerCommit "contract sourceCommit"
Assert-ExactString $external.version $expectedVersion "contract version"
Assert-ExactString $external.manifest $expectedManifest "contract manifest"
Assert-ExactString $external.skillsRoot $expectedSkillsRoot "contract skillsRoot"
Assert-ExactString $external.provenance $evidenceRoot "contract provenance"
$candidateSkills = @($external.skills)
if ($candidateSkills.Count -ne $expectedSkills.Count) {
    throw "The candidate skill inventory does not match the trusted contract."
}
for ($index = 0; $index -lt $expectedSkills.Count; $index++) {
    Assert-ExactString $candidateSkills[$index] $expectedSkills[$index] "contract skill[$index]"
}

$manifestBytes = Get-GitBlobBytes -Repository $producerRoot -ObjectSpec "${expectedProducerCommit}:$expectedManifest"
$manifestHash = Get-Sha256 $manifestBytes
Assert-ExactString $external.manifestSha256 $manifestHash "contract manifestSha256"
$manifest = ConvertFrom-Utf8Json $manifestBytes
Assert-ExactString $manifest.name "concertable" "producer manifest name"
Assert-ExactString $manifest.version $expectedVersion "producer manifest version"
Assert-ExactString $manifest.repository $producerUrl "producer manifest repository"

$provenance = ConvertFrom-Utf8Json (Get-GitBlobBytes -Repository $consumerRoot -ObjectSpec "${CandidateSha}:${evidenceRoot}/provenance.json")
$producerTree = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}^{tree}").Trim()
$producerManifestBlob = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}:$expectedManifest").Trim()
$candidateManifestBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:${evidenceRoot}/plugin.json").Trim()
Assert-ExactString $provenance.sourceCommit $expectedProducerCommit "provenance sourceCommit"
Assert-ExactString $provenance.rootTree $producerTree "provenance rootTree"
Assert-ExactString $provenance.manifestBlob $producerManifestBlob "provenance manifestBlob"
if ($candidateManifestBlob -ne $producerManifestBlob) {
    throw "The candidate provenance manifest snapshot does not match the authenticated producer."
}

foreach ($skill in $expectedSkills) {
    $producerPath = "$expectedSkillsRoot/$skill/SKILL.md"
    $candidatePath = "$evidenceRoot/skills/$skill/SKILL.md"
    $skillBytes = Get-GitBlobBytes -Repository $producerRoot -ObjectSpec "${expectedProducerCommit}:$producerPath"
    $skillHash = Get-Sha256 $skillBytes
    $producerBlob = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}:$producerPath").Trim()
    $candidateBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:$candidatePath").Trim()
    Assert-ExactString $external.skillSha256.$skill $skillHash "contract skillSha256.$skill"
    Assert-ExactString $provenance.skillBlobs.$skill $producerBlob "provenance skillBlobs.$skill"
    if ($candidateBlob -ne $producerBlob) {
        throw "The candidate provenance snapshot for $skill does not match the authenticated producer."
    }
}

$identity = Invoke-CheckedGh api user | Out-String | ConvertFrom-Json
if ($identity.login -cne $attesterLogin -or [int64] $identity.id -ne $attesterId) {
    throw "GitHub CLI is not authenticated as the approved attester."
}

$evidenceBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:${evidenceRoot}/provenance.json").Trim()
$description = "agent-standards@$($expectedProducerCommit.Substring(0, 12)); evidence $($evidenceBlob.Substring(0, 12))"
$targetUrl = "$producerUrl/commit/$expectedProducerCommit"
$body = [ordered]@{
    state = "success"
    context = $statusContext
    description = $description
    target_url = $targetUrl
} | ConvertTo-Json -Compress
$status = $body | & $ghExecutable api --method POST "repos/$consumerRepository/statuses/$CandidateSha" --input - | Out-String | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    throw "Failed to post the repository-bound status."
}
if ($status.state -ne "success" -or
    $status.context -cne $statusContext -or
    $status.description -cne $description -or
    $status.target_url -cne $targetUrl -or
    $status.creator.login -cne $attesterLogin -or
    [int64] $status.creator.id -ne $attesterId) {
    throw "GitHub returned a status that does not match the attestation contract."
}

Write-Output "Posted trusted $statusContext status $($status.id) for $consumerRepository@$CandidateSha."
