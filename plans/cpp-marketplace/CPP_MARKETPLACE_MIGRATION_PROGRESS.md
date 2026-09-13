# Layered C++ marketplace migration progress

- Plan: `plans/cpp-marketplace/CPP_MARKETPLACE_MIGRATION_PLAN.md`
- Roadmap: `plans/cpp-marketplace/CPP_MARKETPLACE_ROADMAP.md`
- Roadmap item: `cpp-marketplace/layered-migration`
- Worktree: `C:\Users\tommy\source\repos\cpp\windows\cpp-agents`
- Branch: `Feature/Layered-Cpp-Marketplace`
- PR: https://github.com/tomjseery/cpp-agents/pull/2 (draft; final trusted attestation, review, and merge next)
- Dependency/package gates: cpp-agents must merge before windows-agents deprecation or installed/consumer configuration changes
- Last reconciled: 2026-09-14 from repository, installed marketplace, consumer inventory, and provenance bootstrap delivery

## Current state

Phase 1 implementation and aggregate review remediation are complete locally. cpp-agents now authors generic, Windows, and GCC standards once and generates the `base`, `windows`, and `gcc` public payloads plus two time-bounded in-marketplace aliases. Routes and detection use a composable ordered layer set and the canonical `concertable:*` workflow namespace. Offline signed evidence and the authenticated local release gate are complete. Reviewed bootstrap PRs #3 and #4 placed the no-secret exact-head gate and its data-only attester on canonical `main`; both are now integrated into the producer branch.

## Next Steps

Publish the reconciled producer head, invoke the trusted attester from an exact clean `main` checkout, require exact-head CI and provenance green, close R22-R25 through incremental review, then merge cpp-agents before beginning windows-agents deprecation. Earlier PR CI run 34787644835 and provenance run 34787643014 attempt 2 proved the gate mechanics at `5b409b25b5696a6c96779e22c556255dd1c33fb4`; the final head must receive its own evidence.

Scope: whole plan through all remaining phases and terminal delivery.
Current slice: Phase 1 immutable candidate, review, and cpp-agents delivery.
Remaining scope: cpp-agents review/merge, windows-agents deprecation delivery, installed configuration migration, all consumer route/configuration migrations, and closeout.
Done when: all three public plugins are delivered and verified in Codex and Claude, windows-agents is safely deprecated, every discovered consumer maps to the correct layers, old-name survivors are classified, and the migration plan is closed.

## Completed work

- Inspected cpp-agents and windows-agents source/manifests/hooks/generators/tests/docs/CI; fetched current remotes.
- Inspected the current installed Codex and Claude plugin configuration and the published `concertable@agent-standards` identity.
- Inventoried current C++ route consumers: parent C++ workspace, note-cli, icon-dropper, wifi-toggle, and winwrap.
- Implemented the canonical three-layer marketplace, migrated Windows source, retained generated aliases through 2027-03-31, and added `AGENTS.md`/`CLAUDE.md`, migration, architecture, release, route, dependency, identifier, and activation validation.

## Verification

- Generated payload check: 62 files current from 11 skills and 11 documents.
- Route generator: canonical generic/GCC/Windows cases, composed Windows+GCC layers, and legacy kind normalization passed.
- Tests: 12 session-detection tests and 10 marketplace/dependency/identifier contract tests passed, including immutable source evidence and verification against the real pinned `concertable` 0.1.6 checkout.
- Codex plugin validator passed for all five canonical/compatibility payloads; Claude plugin and marketplace validation passed.
- `git diff --check` passed.

## Reviews

The initial full review and two incremental repair reviews produced fourteen findings, all repaired. A clean incremental pass approved `e5f083b9fcdc1427a166a00cf7ff34f3e002d2f2`; the delivery preflight then required an aggregate origin/main review of the review-result commit. That aggregate pass through `7cb9d9e589ac819561bb530eb8fb3d9a4ea6c1c3` found two consistency gaps—uppercase write-time routes and retired identities in the canonical hook—and both are repaired. The canonical work order is `reviews/Feature-Layered-Cpp-Marketplace.md`; one final aggregate pass will establish the exact delivery watermark.

## Decisions, discoveries, blockers, and deviations

- The local agent-standards checkout was behind `origin/main`; canonical identity evidence came from fetched `origin/main` and the installed `0.1.6` package, which agree.
- Plugin manifests expose no native dependency/alias field in the supported schema, so layer dependencies and compatibility aliases require repository-owned metadata plus validation and documentation.
- Winwrap had a pre-existing untracked `.codex/` directory before this migration; preserve it and do not sweep it into unrelated commits.
- PR #2 run 34781877587 failed because the current-repository `GITHUB_TOKEN` cannot read the separate private `Concertable/agent-standards` repository. The contract now carries the exact source commit plus an offline-verifiable GitHub signature, signed tree path, manifest blob, and required skill blobs, so CI proves provenance without a cross-repository secret; local release validation also compares hashes against the real checkout.
- The organization policy disables deploy keys, so no deploy key or Actions secret was retained. Bootstrap PR #3 merged the reviewed `pull_request_target` status verifier at `82ff5c1b7fda627935d5f5b38b9371c69d8c91a8`; authenticated source validation remains local to the approved maintainer, and the trusted workflow verifies its exact-head status contract.
- Review found that a candidate-owned attester would execute candidate Python under the maintainer credential. Bootstrap PR #4 replaced it with a trusted `main` attester that treats the candidate as Git data, pins all protected objects, and binds the producer commit to authenticated canonical ancestry; it merged at `e340081cfefc8f89f60b2cbf74c0e370626cc8a5` after explicit approval of the documented root-rotation exception.
- GitHub returned 403 for both branch-protection and ruleset APIs because this private repository's current plan does not support them. `TECH_DEBT.md` records the objective enforcement condition; until then, delivery treats the green trusted gate as a manual merge precondition.
