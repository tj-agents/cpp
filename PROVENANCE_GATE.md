# External contract provenance gate

The `External contract provenance / repository-binding` check protects changes to the external `concertable` skill contract without granting `cpp-agents` a persistent credential for the private producer repository.

The check runs as `pull_request_target`, reads its workflow from the trusted default branch, validates the canonical pull-request repository and exact head SHA, and compares base/head Git objects without checking out or executing pull-request content. A protected change requires the newest exact `agent-standards/provenance` commit status to have been posted by GitHub user `tomjseery` (immutable user id `183629855`) for that head. The status issuer is responsible for authenticating `Concertable/agent-standards`, verifying its pinned source and signed evidence, and only then marking the consumer head successful.

## One-time bootstrap order

1. Review and merge the PR that first adds this workflow. `pull_request_target` cannot run a workflow that is not yet on the default branch, so this introduction PR is explicitly the sole unprotected bootstrap.
2. On the producer migration PR, run the repository attestation script against the pinned private checkout and rerun the new gate if its initial missing-status run failed.
3. Confirm the gate succeeds from the default-branch workflow.
4. Add `External contract provenance / repository-binding` to the `main` branch's required checks and require branches to be up to date before merging. Do not mark the bootstrap PR itself as protected retroactively.

This repository must use direct, strictly up-to-date pull-request merges while this check is required. Do not enable GitHub's merge queue: queue entries are synthetic `merge_group` commits, while the security boundary depends on a trusted `pull_request_target` workflow and an attestation bound to the exact PR head. A merge-group workflow would execute a workflow tree that includes pull-request changes and would therefore weaken that boundary.

Fork PRs remain supported when they do not change protected trust-contract paths. Their changed-file inventory is read through GitHub's paginated API and must be complete; oversized inventories fail closed. A protected trust-contract change must be made on a branch in the canonical repository so the approved maintainer can attest the exact commit there.

Future changes to the contract, evidence, verifier, attestation script, or ordinary CI require a new exact-head attestation. Updates to the trusted producer commit therefore use two PRs: first update and review this default-branch gate's expected producer identity, then change the package contract under the new gate.

## Trust and recovery

This mechanism trusts the approved maintainer's GitHub identity and ability to create commit statuses. Anyone controlling that credential can forge an attestation. If the credential is compromised, revoke it in GitHub immediately, post a failing `agent-standards/provenance` status on affected heads, rotate the attester identity through a separately reviewed bootstrap change, and re-attest every open protected PR. If the login changes but the immutable user id does not, update the expected login in its own reviewed gate change before issuing further attestations.

GitHub status history is the durable audit log. A new commit produces a new SHA and cannot reuse an earlier status. The gate rejects case-colliding status names, colliding check-run names, wrong creators, stale descriptions, wrong producer targets, and evidence from a different head.
