# Layered C++ marketplace migration plan

## Outcome

Make `tomjseery/cpp-agents` the single source and marketplace for composable C++ technical standards with the public plugins `base`, `windows`, and `gcc`, while preserving existing installations through an explicit, time-bounded compatibility path and keeping `Concertable/agent-standards` responsible only for workflow/process standards.

## Constraints

- Author every generic, Windows-specific, and GCC/Linux rule exactly once under this repository's `standards/` tree; plugin and compatibility copies must be generated and drift-checked.
- Use the published `concertable@agent-standards` skill namespace for workflow routes.
- Do not edit generated plugin caches or Winwrap product code.
- Do not update installed or consumer configuration until the new cpp-agents packages are published and verified.
- Validate both Codex and Claude Code marketplace/install behavior.
- Keep the migration recoverable across the cpp-agents, windows-agents, and consumer delivery boundaries.

## Phase 1 - Publish the layered cpp-agents marketplace (implemented locally)

Migrate the Windows standards source into `standards/windows`, rename the authored GCC domain to `standards/gcc`, and generate the `base`, `windows`, and `gcc` plugin payloads. Retain only the minimum generated legacy payloads needed for a documented transition, with an explicit removal date and no second authored rule source.

Update repository instructions (`AGENTS.md` and `CLAUDE.md`), architecture, install/migration documentation, manifests, hook detection, route generation, validation, CI, and release metadata. Validation must reject unknown skill identifiers, missing declared layer dependencies, stale public names outside an explicit compatibility allowlist, generated drift, and wrong portable/Windows/GCC activation.

Consumption contract: after merge, Codex and Claude Code can install `base@cpp-agents`, `windows@cpp-agents`, and `gcc@cpp-agents`; generated routes use `base:*`, `windows:*`, `gcc:*`, and `concertable:*`; `windows` and `gcc` declare and document their dependency on `base`.

Verification gate: generator self-tests, hook tests, marketplace contract tests, generated-file check, plugin validation for every public and compatibility plugin, old-name classification check, clean-tree regeneration check, and both marketplace parsers/installers exercised against the candidate.

## Phase 2 - Deliver and verify cpp-agents

Review the immutable branch candidate, resolve findings, push one stable head, open the cpp-agents PR, own exact-head CI to green, merge it, and verify the marketplace at the merged revision before any installed configuration changes.

Consumption contract: the merged cpp-agents default branch is the authoritative source revision used by the deprecation repository and consumers.

Verification gate: merged commit reachable from `origin/main`, CI green for that exact head, Codex marketplace refresh sees the three public names, and Claude marketplace refresh sees the same three names plus any documented compatibility entries.

## Phase 3 - Deprecate windows-agents safely

Convert `tomjseery/windows-agents` into a clear forwarding/deprecation repository only after Phase 2 is available. Preserve `windows-standards@windows-agents` for the documented compatibility window without retaining an independently authored Windows rules corpus; tie any delivered compatibility payload mechanically to the published cpp-agents source and document its removal date and migration commands.

Consumption contract: existing installations keep working during the compatibility window, while every new install path points to `windows@cpp-agents`.

Verification gate: generated drift check proves the compatibility payload corresponds to its declared cpp-agents source, both harness manifests remain valid, old-name occurrences are classified, CI is green, and the deprecation PR is merged.

## Phase 4 - Migrate installed and repository consumers

Only after the new packages are merged and verified, install/enable the new plugins in Codex and Claude Code, migrate user configuration, then update every discovered C++ consumer route and repository instruction/configuration. The current inventory includes the parent C++ workspace, `note-cli` as GCC/Linux, and `icon-dropper`, `wifi-toggle`, and `winwrap` as native Windows; re-scan before editing so newly discovered consumers are included.

Consumption contract: generic C++ routes load `base`, native Windows routes load `base + windows`, GCC/Linux routes load `base + gcc`, and workflow/doc routes load `concertable`.

Verification gate: route generation/check passes per consumer kind; each repository has coherent `AGENTS.md` and `CLAUDE.md` setup appropriate to its existing guidance model; no product source changes are present; installed Codex/Claude plugin lists show the new packages enabled; and old installations are disabled or removed according to the migration guide.

## Phase 5 - Close out

Run the cross-repository old-name grep and classify every survivor as a compatibility alias, time-bounded deprecation, intentional historical record, or error. Record any unresolved problem in the owning `TECH_DEBT.md`; otherwise remove this plan and its ledger after all PRs, installation changes, and consumer checks are terminal.

Verification gate: clean working trees except pre-existing user changes, all required PRs merged, all remote checks green, installed configuration current, consumer route activation proven, and the final Winwrap planning prompt derived without starting product implementation.
