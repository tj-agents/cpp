param(
    [Parameter(Mandatory = $true)]
    [string] $AgentStandardsSource
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$consumerRepository = "tomjseery/cpp-agents"
$producerRepository = "Concertable/agent-standards"
$expectedProducerCommit = "93d8bd57fbfbd793acdebe542f7ae270a0c1d2a1"
$attesterLogin = "tomjseery"
$attesterId = 183629855
$statusContext = "agent-standards/provenance"
$trustPaths = @(
    ".agents/attest-external-contract.ps1",
    ".agents/plugins/skill-contract.json",
    ".agents/tests/test_marketplace_contract.py",
    ".github/workflows/ci.yml",
    ".github/workflows/provenance-gate.yml",
    "contracts/concertable-0.1.6"
)

function Invoke-CheckedGit {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $Arguments)
    $output = & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($Arguments -join ' ')"
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

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = (Resolve-Path -LiteralPath $AgentStandardsSource).Path
$previousSource = [Environment]::GetEnvironmentVariable("AGENT_STANDARDS_SOURCE", "Process")

Push-Location $repositoryRoot
try {
    $head = (Invoke-CheckedGit rev-parse HEAD).Trim()
    if ($head -notmatch "^[0-9a-f]{40}$") {
        throw "cpp-agents HEAD is not a full Git commit SHA."
    }

    & git cat-file -e "${head}:.agents/attest-external-contract.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "The attestation script is not present in the exact commit being attested."
    }

    & git diff --quiet HEAD -- @trustPaths
    if ($LASTEXITCODE -ne 0) {
        throw "Trust-contract paths differ from HEAD; commit them before attesting."
    }
    & git diff --cached --quiet HEAD -- @trustPaths
    if ($LASTEXITCODE -ne 0) {
        throw "Staged trust-contract paths differ from HEAD; commit them before attesting."
    }

    $contractText = (Invoke-CheckedGit show "${head}:.agents/plugins/skill-contract.json") -join "`n"
    $contract = $contractText | ConvertFrom-Json
    $external = $contract.externalPlugins.concertable
    if ($external.repository -ne "https://github.com/$producerRepository") {
        throw "The committed producer repository does not match the canonical contract."
    }
    if ($external.sourceCommit -ne $expectedProducerCommit) {
        throw "The committed producer SHA does not match the trusted gate."
    }

    $identity = (Invoke-CheckedGh api user | Out-String | ConvertFrom-Json)
    if ($identity.login -cne $attesterLogin -or [int64] $identity.id -ne $attesterId) {
        throw "GitHub CLI is not authenticated as the approved attester."
    }

    $remoteHead = (Invoke-CheckedGh api "repos/$consumerRepository/commits/$head" --jq ".sha").Trim()
    if ($remoteHead -ne $head) {
        throw "Push the exact cpp-agents HEAD before attesting."
    }
    $producerHead = (Invoke-CheckedGh api "repos/$producerRepository/commits/$expectedProducerCommit" --jq ".sha").Trim()
    if ($producerHead -ne $expectedProducerCommit) {
        throw "The pinned producer commit is not present in the canonical private repository."
    }

    [Environment]::SetEnvironmentVariable("AGENT_STANDARDS_SOURCE", $sourceRoot, "Process")
    & python -m unittest discover -s .agents/tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "External contract validation failed; no status was posted."
    }

    $headAfterValidation = (Invoke-CheckedGit rev-parse HEAD).Trim()
    if ($headAfterValidation -ne $head) {
        throw "cpp-agents HEAD moved during validation; no status was posted."
    }
    & git diff --quiet HEAD -- @trustPaths
    if ($LASTEXITCODE -ne 0) {
        throw "Trust-contract paths changed during validation; no status was posted."
    }
    & git diff --cached --quiet HEAD -- @trustPaths
    if ($LASTEXITCODE -ne 0) {
        throw "Staged trust-contract paths changed during validation; no status was posted."
    }

    $evidenceBlob = (Invoke-CheckedGit rev-parse "${head}:contracts/concertable-0.1.6/provenance.json").Trim()
    if ($evidenceBlob -notmatch "^[0-9a-f]{40}$") {
        throw "The committed provenance blob is invalid."
    }
    $description = "agent-standards@$($expectedProducerCommit.Substring(0, 12)); evidence $($evidenceBlob.Substring(0, 12))"
    $targetUrl = "https://github.com/$producerRepository/commit/$expectedProducerCommit"
    $body = [ordered]@{
        state = "success"
        context = $statusContext
        description = $description
        target_url = $targetUrl
    } | ConvertTo-Json -Compress
    $status = ($body | gh api --method POST "repos/$consumerRepository/statuses/$head" --input - | Out-String | ConvertFrom-Json)
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

    Write-Output "Posted $statusContext status $($status.id) for $consumerRepository@$head."
}
finally {
    [Environment]::SetEnvironmentVariable("AGENT_STANDARDS_SOURCE", $previousSource, "Process")
    Pop-Location
}
