# Layered C++ marketplace migration progress

- Plan: `plans/cpp-marketplace/CPP_MARKETPLACE_MIGRATION_PLAN.md`
- Roadmap: `plans/cpp-marketplace/CPP_MARKETPLACE_ROADMAP.md`
- Roadmap item: `cpp-marketplace/layered-migration`
- Worktree: `C:\Users\tommy\source\repos\cpp\windows\cpp-agents`
- Branch: `Feature/Layered-Cpp-Marketplace`
- PR: https://github.com/tomjseery/cpp-agents/pull/2 (draft; fixing first remote CI result)
- Dependency/package gates: cpp-agents must merge before windows-agents deprecation or installed/consumer configuration changes
- Last reconciled: 2026-09-13 from repository, installed marketplace, and consumer inventory

## Current state

Phase 1 implementation and aggregate review remediation are complete locally. cpp-agents now authors generic, Windows, and GCC standards once and generates the `base`, `windows`, and `gcc` public payloads plus two time-bounded in-marketplace aliases. Routes and detection use a composable ordered layer set and the canonical `concertable:*` workflow namespace. PR #2 exposed that a repository-scoped Actions token cannot check out the separate private agent-standards repository; the fixing candidate replaces that remote checkout with an immutable source lock while retaining real-source local verification.

## Next Steps

Review and push the CI fix, own exact-head PR CI to green, then merge the cpp-agents producer before beginning windows-agents deprecation.

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
- PR #2 run 34781877587 failed because the current-repository `GITHUB_TOKEN` cannot read the separate private `Concertable/agent-standards` repository. The contract now records exact source commit, version, manifest hash, and routed-skill hashes so CI remains deterministic without a cross-repository secret; local release validation still checks those hashes against the real checkout.
