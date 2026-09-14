# External contract provenance gate

The `External contract provenance / repository-binding` check protects changes to the external `concertable` skill contract without granting `cpp-agents` a persistent credential for the private producer repository.

The check runs as `pull_request_target`, reads its workflow from the trusted default branch, validates the canonical pull-request repository and exact head SHA, and compares base/head Git objects without checking out or executing pull-request content. A protected change requires the newest exact `agent-standards/provenance` commit status to have been posted by GitHub user `tomjseery` (immutable user id `183629855`) for that head. The status issuer is responsible for authenticating `Concertable/agent-standards`, verifying its pinned source and signed evidence, and only then marking the consumer head successful.

## One-time bootstrap order

1. Review and merge the PR that first adds this workflow. `pull_request_target` cannot run a workflow that is not yet on the default branch, so this introduction PR is explicitly the sole unprotected bootstrap.
2. Add and review the attestation script on the default branch in a separate bootstrap PR. The script must inspect candidate Git objects as data; it must never execute candidate-owned code while the maintainer credential is available.
3. From an exact, clean checkout of canonical `main`, run that trusted script against the producer migration's exact pushed SHA and pinned private checkout, then rerun the gate if its initial missing-status run failed.
4. Confirm the gate succeeds from the default-branch workflow.
5. Where the repository plan supports it, add `External contract provenance / repository-binding` to the `main` branch's required checks and require branches to be up to date before merging. Do not mark either bootstrap PR itself as protected retroactively. Until private-repository rulesets are available, a green gate is a mandatory maintainer merge precondition; [TECH_DEBT.md](TECH_DEBT.md) owns the objective enforcement follow-up.

This repository must use direct, strictly up-to-date pull-request merges while this check is required. Do not enable GitHub's merge queue: queue entries are synthetic `merge_group` commits, while the security boundary depends on a trusted `pull_request_target` workflow and an attestation bound to the exact PR head. A merge-group workflow would execute a workflow tree that includes pull-request changes and would therefore weaken that boundary.

Fork PRs remain supported when they do not change protected trust-contract paths. Their changed-file inventory is read through GitHub's paginated API and must be complete; oversized inventories fail closed. A protected trust-contract change must be made on a branch in the canonical repository so the approved maintainer can attest the exact commit there.

Future changes to the contract, evidence, verifier, or ordinary CI require a new exact-head attestation. The trusted script changes to its own canonical-main directory, resolves Git and GitHub CLI once to absolute application paths outside the candidate, requires candidate trust tools to match canonical `main`, pins every other protected candidate object, binds the producer commit to authenticated reachability from canonical `main`, and validates exact candidate blobs against the authenticated producer checkout directly. Candidate executables, scripts, tests, hooks, and generators are never invoked.

The credential-free attester safety suite parses the trusted script and rejects uncaptured Git or GitHub CLI launches on every CI platform. Its dedicated Windows job additionally proves that candidate-owned executables on `PATH` are rejected and that executables placed only in the candidate current directory are not selected.

Changing the attester, gate workflow, trusted producer identity, or approved object pins is a root-of-trust rotation, not an ordinary two-PR update. Use a dedicated first PR containing only the trust-root change and its documentation, freeze it, and complete independent security, contract, and failure-mode review. If branch protection is available, an administrator temporarily removes only this required check, merges that exact reviewed head after its remaining checks pass, and restores the requirement immediately; record both settings transitions in the PR. On plans without branch protection, the same reviewed bootstrap is the sole manual exception. The next protected PR must exercise the new attester and trusted workflow successfully before ordinary delivery resumes. Never use this procedure to bypass a red check on a non-root change.

## Trust and recovery

This mechanism trusts the approved maintainer's GitHub identity and ability to create commit statuses. Anyone controlling that credential can forge an attestation. If the credential is compromised, revoke it in GitHub immediately, post a failing `agent-standards/provenance` status on affected heads, rotate the attester identity through a separately reviewed bootstrap change, and re-attest every open protected PR. If the login changes but the immutable user id does not, update the expected login in its own reviewed gate change before issuing further attestations.

GitHub status history is the durable audit log. A new commit produces a new SHA and cannot reuse an earlier status. The gate rejects case-colliding status names, colliding check-run names, wrong creators, stale descriptions, wrong producer targets, and evidence from a different head.
