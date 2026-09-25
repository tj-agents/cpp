# C++ Naming Guidance Delivery Plan

## Authorization and outcome

The handoff authorizes a reviewable change that closes two canonical C++ guidance gaps,
regenerates all owned aliases and packages, completes the repository-required validation,
and, where access permits, commits, pushes, and opens a pull request. It does not authorize
editing SandboxHwid or WinWrap, merging the pull request, or publishing a plugin release.

## Scope

- Add semantic local-variable naming guidance to
  `.agents/base/contract/style/SKILL.md`.
- Clarify justified infallible static-factory naming for passive records in
  `.agents/base/contract/domain-design/SKILL.md`.
- Keep authored changes under `.agents/`; update generated outputs only through the
  repository generator.
- Bump both affected host manifests, record package versions, and preserve compatibility
  packages and historical signed provenance.

## Execution and acceptance

1. Inspect nearby authored examples, generated aliases, source/package mappings, manifests,
   validation entry points, and current version records.
2. Make the two concise canonical rule changes without introducing blanket type-copy naming,
   mandatory factories, or claims that `create` validates arbitrary enum casts.
3. Bump the relevant manifest versions, regenerate, and record package versions.
4. Run the generator check, route self-test, hook tests, marketplace and attester tests, both
   host validators when available, and G++, MSVC, and Win32 scaffold acceptance tests with
   real builds where their toolchains exist.
5. Review the complete diff, create a focused commit, push the branch, and open a reviewable
   pull request. Do not merge or publish.

## Progress

- [x] Read the handoff, repository instructions, README, lifecycle, worktree, branching, and
  routed C++ standards skills.
- [x] Verified clean `main` and fetched `origin/main` at
  `8a749a1400cd7985ea970d34b464be8a3490a5c9`.
- [x] Verified no open pull request blocks branch creation.
- [x] Created `Docs/Clarify-Naming-Guidance` in the isolated worktree at
  `C:\Users\tommy\source\repos\tj-agents\cpp\.worktrees\Docs-Clarify-Naming-Guidance`.
- [x] Inspected source/package mappings, manifests, package-version records, nearby
  examples, generated aliases, validation workflows, and current versions.
- [x] Added both canonical rules and bumped the six affected host manifests. The reviewed
  final payloads are `cpp` 0.4.4 and `base` / `cpp-standards` 0.7.4; the initial immutable
  candidate remains recorded as 0.4.3 / 0.7.3.
- [x] Regenerated 296 files from 18 definitions and recorded both immutable candidate and
  review-fix hashes for `cpp`, `base`, and `cpp-standards`.
- [x] Passed the generated-content check, route self-test, 11 hook tests, and 72 repository
  tests (one documented optional live-source comparison skipped). The repository suite ran
  real G++, MSVC, MinGW/Win32, marketplace, attester, package-version, and scaffold checks.
- [x] Passed Claude Code strict validation for the marketplace and all nine packages.
- [x] Verified the repository's `AGENTS.md` / `CLAUDE.md` pair in both directions.
- [x] Full review of candidate `e39ecce` found one contradiction: the nearby decode
  example still used the generic `record` local. The remediation renames it to `identity`
  and advances the affected package versions to `cpp` 0.4.4 and compatibility 0.7.4.
- [x] Re-ran the generator check, route self-test, 11 hook tests, 72 repository tests, and
  strict Claude marketplace/package validation successfully after the remediation.
- [x] Committed the initial candidate as `e39ecce`, the remediation as `f7c2e62`, and
  completed the incremental review of `e39ecce..f7c2e62` with no new findings.
- [ ] Push the branch, open the pull request, and complete remote validation.

The installed Codex host has `cpp-agents` bound to the remote marketplace. Replacing that
user-level source with this unpublished worktree would be disruptive, so the exact Codex
install validator remains assigned to the pull request's CI job after push.

## Current next action

Push the reviewed branch, open the pull request, and own its Codex validation and other CI
checks to completion without merging or publishing a plugin release.
