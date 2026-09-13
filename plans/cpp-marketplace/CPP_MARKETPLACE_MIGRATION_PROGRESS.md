# Layered C++ marketplace migration progress

- Plan: `plans/cpp-marketplace/CPP_MARKETPLACE_MIGRATION_PLAN.md`
- Roadmap: `plans/cpp-marketplace/CPP_MARKETPLACE_ROADMAP.md`
- Roadmap item: `cpp-marketplace/layered-migration`
- Worktree: `C:\Users\tommy\source\repos\cpp\windows\cpp-agents`
- Branch: `Feature/Layered-Cpp-Marketplace`
- PR: not opened
- Dependency/package gates: cpp-agents must merge before windows-agents deprecation or installed/consumer configuration changes
- Last reconciled: 2026-09-13 from repository, installed marketplace, and consumer inventory

## Current state

Phase 1 implementation and three completed review-remediation rounds are complete locally. cpp-agents now authors generic, Windows, and GCC standards once and generates the `base`, `windows`, and `gcc` public payloads plus two time-bounded in-marketplace aliases. Routes and detection use a composable ordered layer set and the canonical `concertable:*` workflow namespace. The latest fixing head now needs a clean incremental pass and final validation before delivery.

## Next Steps

Run the incremental review from the frozen candidate through the remediation head, resolve any new findings, complete final local validation, then deliver and merge the cpp-agents PR while owning exact-head CI.

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
- Tests: 12 session-detection tests and 9 marketplace/dependency/identifier contract tests passed, including the pinned real `concertable` 0.1.6 source inventory.
- Codex plugin validator passed for all five canonical/compatibility payloads; Claude plugin and marketplace validation passed.
- `git diff --check` passed.

## Reviews

The full review of `0708f87710211a7726df1a7eccb1da212f9d47d9` requested changes. Its eight findings were repaired in isolated commits. The first incremental review through `91d26fe31e8bcaade1fd187e00bf3f6bf5f37c0d` found four further issues, all repaired. The second incremental review through `f79f78cf168283ed20baa4bbe82c18fdec1a2a27` found exact legacy skill resolution and uppercase path-matching defects; both are repaired. The canonical work order is `reviews/Feature-Layered-Cpp-Marketplace.md`; a clean incremental pass over the third repair range is next.

## Decisions, discoveries, blockers, and deviations

- The local agent-standards checkout was behind `origin/main`; canonical identity evidence came from fetched `origin/main` and the installed `0.1.6` package, which agree.
- Plugin manifests expose no native dependency/alias field in the supported schema, so layer dependencies and compatibility aliases require repository-owned metadata plus validation and documentation.
- Winwrap had a pre-existing untracked `.codex/` directory before this migration; preserve it and do not sweep it into unrelated commits.
