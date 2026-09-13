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

function Invoke-CheckedGit {
    param(
        [Parameter(Mandatory = $true)][string] $Repository,
        [Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments
    )
    $output = & git -C $Repository @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed in ${Repository}: git $($Arguments -join ' ')"
    }
    return $output
}

function Invoke-CheckedGh {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments)
    $output = & gh @Arguments
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
    $start.FileName = "git"
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
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

$trustedRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$consumerRoot = (Resolve-Path -LiteralPath $ConsumerSource).Path
$producerRoot = (Resolve-Path -LiteralPath $AgentStandardsSource).Path

if ($CandidateSha -notmatch "^[0-9a-f]{40}$") {
    throw "CandidateSha must be a full lowercase Git commit SHA."
}

$trustedHead = (Invoke-CheckedGit -Repository $trustedRoot rev-parse HEAD).Trim()
$remoteMain = (Invoke-CheckedGh api "repos/$consumerRepository/git/ref/heads/main" --jq ".object.sha").Trim()
if ($trustedHead -ne $remoteMain) {
    throw "Run the attester from an exact checkout of the canonical main branch."
}
& git -C $trustedRoot diff --quiet HEAD -- .agents/attest-external-contract.ps1
if ($LASTEXITCODE -ne 0) {
    throw "The trusted attester differs from canonical main."
}

Assert-CanonicalRemote -Repository $consumerRoot -ExpectedSlug $consumerRepository
Assert-CanonicalRemote -Repository $producerRoot -ExpectedSlug $producerRepository

$remoteCandidate = (Invoke-CheckedGh api "repos/$consumerRepository/commits/$CandidateSha" --jq ".sha").Trim()
if ($remoteCandidate -ne $CandidateSha) {
    throw "The candidate is not present in the canonical consumer repository."
}

$producerHead = (Invoke-CheckedGit -Repository $producerRoot rev-parse HEAD).Trim()
if ($producerHead -ne $expectedProducerCommit) {
    throw "The producer checkout is not at the trusted commit."
}
$producerRecord = Invoke-CheckedGh api "repos/$producerRepository/commits/$expectedProducerCommit" | Out-String | ConvertFrom-Json
if ($producerRecord.sha -ne $expectedProducerCommit -or -not $producerRecord.commit.verification.verified) {
    throw "The producer commit is absent from the canonical repository or is not verified."
}

$contract = ConvertFrom-Utf8Json (Get-GitBlobBytes -Repository $consumerRoot -ObjectSpec "${CandidateSha}:$contractPath")
$external = $contract.externalPlugins.concertable
if ($external.repository -ne $producerUrl -or
    $external.sourceCommit -ne $expectedProducerCommit -or
    $external.version -ne $expectedVersion -or
    $external.manifest -ne $expectedManifest -or
    $external.skillsRoot -ne $expectedSkillsRoot -or
    (@($external.skills) -join "`0") -cne ($expectedSkills -join "`0")) {
    throw "The candidate external skill contract does not match the trusted contract."
}

$manifestBytes = Get-GitBlobBytes -Repository $producerRoot -ObjectSpec "${expectedProducerCommit}:$expectedManifest"
$manifestHash = Get-Sha256 $manifestBytes
if ($external.manifestSha256 -ne $manifestHash) {
    throw "The candidate manifest hash does not match the authenticated producer."
}
$manifest = ConvertFrom-Utf8Json $manifestBytes
if ($manifest.name -ne "concertable" -or $manifest.version -ne $expectedVersion -or $manifest.repository -ne $producerUrl) {
    throw "The authenticated producer manifest does not match the trusted identity."
}

$provenance = ConvertFrom-Utf8Json (Get-GitBlobBytes -Repository $consumerRoot -ObjectSpec "${CandidateSha}:${evidenceRoot}/provenance.json")
$producerTree = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}^{tree}").Trim()
$producerManifestBlob = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}:$expectedManifest").Trim()
$candidateManifestBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:${evidenceRoot}/plugin.json").Trim()
if ($provenance.sourceCommit -ne $expectedProducerCommit -or
    $provenance.rootTree -ne $producerTree -or
    $provenance.manifestBlob -ne $producerManifestBlob -or
    $candidateManifestBlob -ne $producerManifestBlob) {
    throw "The candidate provenance manifest does not match the authenticated producer tree."
}

foreach ($skill in $expectedSkills) {
    $producerPath = "$expectedSkillsRoot/$skill/SKILL.md"
    $candidatePath = "$evidenceRoot/skills/$skill/SKILL.md"
    $skillBytes = Get-GitBlobBytes -Repository $producerRoot -ObjectSpec "${expectedProducerCommit}:$producerPath"
    $skillHash = Get-Sha256 $skillBytes
    $producerBlob = (Invoke-CheckedGit -Repository $producerRoot rev-parse "${expectedProducerCommit}:$producerPath").Trim()
    $candidateBlob = (Invoke-CheckedGit -Repository $consumerRoot rev-parse "${CandidateSha}:$candidatePath").Trim()
    if ($external.skillSha256.$skill -ne $skillHash -or
        $provenance.skillBlobs.$skill -ne $producerBlob -or
        $candidateBlob -ne $producerBlob) {
        throw "The candidate provenance for $skill does not match the authenticated producer."
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
$status = $body | gh api --method POST "repos/$consumerRepository/statuses/$CandidateSha" --input - | Out-String | ConvertFrom-Json
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
