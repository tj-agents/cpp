# Code review — Feature/Layered-Cpp-Marketplace

> **This file is a work order, not a discussion.** Fix open `[ ]` findings directly and tick each `[x]` as it lands. Record a durable disposition for anything intentionally not fixed.

**Review status:** `complete`
**Judgment:** `changes-requested`
**Reviewed up to commit:** `0708f87710211a7726df1a7eccb1da212f9d47d9`
**Security-reviewed up to commit:** `0708f87710211a7726df1a7eccb1da212f9d47d9`

## Review pass — 2026-09-13 — full

**Candidate base:** `f08caa4396ffc51cc9d9a9d21d419d225f8bdaf3`
**Candidate head:** `0708f87710211a7726df1a7eccb1da212f9d47d9`
**Candidate branch:** `Feature/Layered-Cpp-Marketplace`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:cdd90534c0e691a6fedf25cfc685c4e6fab18e5dffc98e39e9bb26f65fdd7511` `(76 paths)`
**Candidate bundle:** `C:\Users\tommy\source\repos\cpp\windows\cpp-agents\.git\agent-workflow\runs\cpp-marketplace-migration\review\f75bf5d1974c6d1ae245f2ed838a6cc0d71974fb25960beeef68ac8c99fa9bc0`
**Candidate bundle identity:** `sha256:902a6cd1c33b66d1689f252661ac9fa538071d5de97df985e5e0b3ba806e39c6`
**Work-order path:** `reviews/Feature-Layered-Cpp-Marketplace.md`
**Work-order mode:** `new`
**Pass judgment:** `changes-requested`

### Findings

- [x] **R1 — HIGH — layered activation contract** — `.agents/gen_skill_routes.py:15`,
  `.agents/hooks/session_context.py:95`
  The architecture promises that platform layers compose, including `base + windows + gcc`, but the
  generator accepts one mutually exclusive kind and both generator and hook use `if`/`elif`. Represent
  activation as a set/list of layers, retain legacy singular `kind` as input compatibility, and assert
  simultaneous base, Windows, and GCC activation.
  Fixed in the next remediation commit: generated routes now carry an ordered `layers` list, repeated
  `--layer` inputs compose platform layers, legacy `--kind` values remain accepted, and both the route
  self-test and hook tests prove `base + windows + gcc` activation.

- [x] **R2 — HIGH — one rule, one owner** — `standards/cpp/KNOWLEDGE.md:102`,
  `standards/cpp/DIRECTION.md:25`, `standards/cpp/LIBRARIES.md:9`
  The `base` payload still contains Windows-, GCC-, GDB-, and Linux-specific rules, including material
  duplicated by `standards/windows/KNOWLEDGE.md`. Move platform-specific guidance to its owning Windows
  or GCC domain and leave only platform-neutral C++ guidance in `standards/cpp`.
  Fixed in the next remediation commit: base now expresses only neutral systems foundations and
  platform-selected tool categories; GCC/GDB/perf choices and their learning calibration live solely in
  `standards/gcc/TOOLCHAIN.md`, while Windows-specific calibration remains solely in the Windows domain.

- [x] **R3 — HIGH — compatibility installation contract** —
  `plugins/cpp-standards/hooks/session_context.py:92`
  The compatibility alias hook emits only canonical `base:*`, `windows:*`, and `gcc:*` identifiers. An
  existing alias-only installation is therefore told to load plugins that are not installed, including
  `gcc:gcc-toolchain` rather than its shipped legacy alias. Generate a compatibility-specific hook and
  cover the old-only installation path.
  Fixed in the next remediation commit: the single authored hook derives its installed plugin identity;
  the compatibility copy emits only `cpp-standards:*`, `gpp-standards:*`, and the legacy
  `windows-standards:*` namespace, with an old-only regression test.

- [x] **R4 — HIGH — external skill contract provenance** —
  `.agents/plugins/skill-contract.json:2`, `.agents/tests/test_marketplace_contract.py:98`
  Broken external skill validation is self-referential: a hand-authored local assertion is checked against
  generated routes, but not against the installed or source `concertable@agent-standards` package. Pin
  the source/version and validate its actual skill inventory.
  Fixed in the next remediation commit: the external contract now pins the canonical repository,
  `concertable` 0.1.6 manifest, exact source commit, skills root, and skill names; CI checks out that
  commit and the contract test verifies its real manifest and files.

- [x] **R5 — MEDIUM — complete Windows detection** — `.agents/hooks/session_context.py:76`
  Windows marker detection scans only the first 200 tracked C++ files. A native Windows repository whose
  first Win32 marker sorts later is misclassified. Search every tracked candidate efficiently and add a
  regression with the marker after candidate 200.
  Fixed in the next remediation commit: detection examines the complete tracked C++ candidate set and a
  201-file regression proves a final-file Win32 marker selects Windows rather than the Linux host layer.

- [x] **R6 — MEDIUM — Windows CMake ownership route** — `.agents/gen_skill_routes.py:67`
  Windows CMake rules live in `windows:win32-style`, but the Windows build route loads only
  `windows:windows-overview`. Route build files to the owning skill and cover this case in the self-test.
  Fixed in the next remediation commit: Windows build routes now load `windows:win32-style` and the
  self-test asserts the complete base-plus-Windows CMake skill set.

- [x] **R7 — MEDIUM — installable schema validation** — `.github/workflows/ci.yml:12`
  CI does not run the Codex or Claude marketplace/plugin validators that the README claims. Add both
  harness validators for the marketplace and all five generated payloads, or an equivalent checked-in
  schema validator that exercises the same contracts.
  Fixed in the next remediation commit: CI pins Codex 0.154.0 and Claude Code 2.1.268, registers and
  installs all five packages through Codex, and runs Claude's strict marketplace plus per-plugin
  validators. The same five payloads pass the current local Codex and strict Claude validators.

- [x] **R8 — MEDIUM — compatibility expiry enforcement** —
  `.agents/tests/test_marketplace_contract.py:80`
  Alias removal dates are compared with the fixed migration date, so expired aliases continue to pass.
  Compare against the current date or add an equivalent release-time expiry gate.
  Fixed in the next remediation commit: both generation and contract tests compare `removeAfter` with
  the current date and fail once an alias is due for removal.

Validation on the frozen candidate: generated drift check, route self-test, seven hook tests, six
contract tests, all five Codex payload validators, the Claude marketplace validator, and all five Claude
payload validators passed. These checks establish the candidate state but do not resolve the findings
above.
