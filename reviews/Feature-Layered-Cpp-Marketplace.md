# Code review — Feature/Layered-Cpp-Marketplace

> **This file is a work order, not a discussion.** Fix open `[ ]` findings directly and tick each `[x]` as it lands. Record a durable disposition for anything intentionally not fixed.

**Review status:** `complete`
**Judgment:** `changes-requested`
**Reviewed up to commit:** `7cb9d9e589ac819561bb530eb8fb3d9a4ea6c1c3`
**Security-reviewed up to commit:** `7cb9d9e589ac819561bb530eb8fb3d9a4ea6c1c3`

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

## Review pass — 2026-09-13 — incremental

**Candidate base:** `0708f87710211a7726df1a7eccb1da212f9d47d9`
**Candidate head:** `91d26fe31e8bcaade1fd187e00bf3f6bf5f37c0d`
**Candidate branch:** `Feature/Layered-Cpp-Marketplace`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:b4e09369557da637be879c753461f913f976bb9173b47e9fc1810e7a6364cb7c` `(31 paths)`
**Candidate bundle:** `C:\Users\tommy\source\repos\cpp\windows\cpp-agents\.git\agent-workflow\runs\cpp-marketplace-migration\review\26151dd32c2d232b5a42dbe6ee254d81fc45561983ec7039e6bb06815e528fa2`
**Candidate bundle identity:** `sha256:1795e4739f7e58b5253d087a91b65c18498a86753b8adf7b0ca02836b1bc89f2`
**Work-order path:** `reviews/Feature-Layered-Cpp-Marketplace.md`
**Work-order mode:** `append`
**Pass judgment:** `changes-requested`

### Findings

- [x] **R9 — HIGH — installed compatibility-hook identity** —
  `.agents/hooks/session_context.py:129`
  The hook infers its plugin from `parents[1]`, which is the version directory in real Codex and Claude
  caches, so the compatibility payload still emits canonical namespaces after installation. Bake the
  identity into each generated hook or correctly resolve a versioned cache layout, and test that layout
  without injecting the plugin name.
  Fixed in the next remediation commit: generation binds an explicit plugin identity into each hook copy,
  and the regression imports the compatibility hook from a realistic versioned cache path without an
  identity override.

- [x] **R10 — MEDIUM — bounded session detection** — `.agents/hooks/session_context.py:99`
  Removing the 200-file cap changed the hook to synchronous full-file reads across the entire C++ corpus
  under a five-second timeout. Large generic/GCC repositories can lose even base context. Use an efficient,
  bounded repository-wide search while preserving late-file detection coverage.
  Fixed in the next remediation commit: tracked repositories use Git's quiet fixed-string grep, which
  stops at the first match without Python file reads; non-Git fallback reads line-by-line. Tests cover both
  a 100,000-path fast-path inventory and a marker in source 201.

- [x] **R11 — MEDIUM — compatibility end-date semantics** —
  `.agents/sync-generated.ps1:272`, `.agents/tests/test_marketplace_contract.py:82`
  Documentation says aliases remain through and are removed after 2027-03-31, but validation rejects them
  on March 31. Align the checks so the documented final supported day remains valid.
  Fixed in the next remediation commit: March 31 remains valid and both gates fail only after the declared
  final supported day.

- [x] **R12 — MEDIUM — alias payload namespace closure** —
  `plugins/cpp-standards/standards/cpp/BUILD.md:38`
  Compatibility payload documents retain canonical-only `base:*`, `windows:*`, and `gcc:*` cross-references
  unavailable to old-only installations. Generate compatibility namespace rewrites and validate that alias
  payloads contain no canonical-only skill identifiers.
  Fixed in the next remediation commit: compatibility metadata owns namespace and selector mappings;
  generation applies them to alias standards, skills, and hooks; a payload-wide test rejects canonical
  skill identifiers in either compatibility package.

Validation on the frozen remediation range: generated drift, route self-test, ten hook tests, eight local
contract tests, five Codex validators, strict Claude marketplace validation, and five strict Claude plugin
validations passed. The external-source test is exercised by CI with its pinned checkout. The passing gates
did not cover the four defects above.

## Review pass — 2026-09-13 — incremental

**Candidate base:** `91d26fe31e8bcaade1fd187e00bf3f6bf5f37c0d`
**Candidate head:** `f79f78cf168283ed20baa4bbe82c18fdec1a2a27`
**Candidate branch:** `Feature/Layered-Cpp-Marketplace`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:0c1361d830fd4d71a76c6b2f42dc571df931e0aa65f232125b9f56fa024e3f46` `(12 paths)`
**Candidate bundle:** `C:\Users\tommy\source\repos\cpp\windows\cpp-agents\.git\agent-workflow\runs\cpp-marketplace-migration\review\1836ebce7c0e467cd19f2dd91c4c05e85bc276fb90ece2cad0cb94f5bea6ce77`
**Candidate bundle identity:** `sha256:4be48043a26132c7b6da1a3c67fee9995aac4dba092cf53c8b5454d1c76a5edc`
**Work-order path:** `reviews/Feature-Layered-Cpp-Marketplace.md`
**Work-order mode:** `append`
**Pass judgment:** `changes-requested`

### Findings

- [x] **R13 — HIGH — exact compatibility skill resolution** —
  `plugins/cpp-standards/standards/cpp/KNOWLEDGE.md:118`
  Namespace rewriting produces `gpp-standards:gcc-toolchain`, but that alias exposes only
  `gpp-standards:gpp-toolchain`. Rewrite complete qualified identifiers and validate every alias-qualified
  reference against the actual generated compatibility skill inventories.
  Fixed in the next remediation commit: compatibility metadata rewrites the full GCC identifier before
  namespace rewrites, records the legacy Windows inventory, and validates every qualified identifier in
  alias documents and hooks against the generated/local or declared legacy plugin inventory.

- [x] **R14 — MEDIUM — case-insensitive source path matching** —
  `.agents/hooks/session_context.py:105`
  C++ candidates recognize extensions case-insensitively, but Git grep pathspecs contain only lowercase
  suffixes. On a case-sensitive checkout, an uppercase `.CPP` marker is missed and return code 1 suppresses
  fallback scanning. Make Git path matching case-insensitive or search the exact candidate inventory, and
  add an uppercase-extension regression.
  Fixed in the next remediation commit: Git pathspecs use `icase` magic and a real temporary Git repository
  proves that a tracked `MAIN.CPP` with an uppercase Win32 include is detected.

Validation on the frozen second repair range: generated drift, eleven hook tests, nine contract tests,
and both harness validators passed. Those tests did not resolve qualified alias identifiers or exercise
uppercase Git path matching.

## Review pass — 2026-09-13 — incremental

**Candidate base:** `f79f78cf168283ed20baa4bbe82c18fdec1a2a27`
**Candidate head:** `e5f083b9fcdc1427a166a00cf7ff34f3e002d2f2`
**Candidate branch:** `Feature/Layered-Cpp-Marketplace`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:9dd9d0a1a7591ba34db2eb02af828113f8272a37bd4afb5b4a32b9debca3154e` `(11 paths)`
**Candidate bundle:** `C:\Users\tommy\source\repos\cpp\windows\cpp-agents\.git\agent-workflow\runs\cpp-marketplace-migration\review\2d7f6bd695f27357121ff94b4e3b41e5cb217772341dd17e95eaaf7dba6211b6`
**Candidate bundle identity:** `sha256:0c9868d3d698bce6c11c3a38ae57260375659757adc5e930f47a69f43bbdee3b`
**Work-order path:** `reviews/Feature-Layered-Cpp-Marketplace.md`
**Work-order mode:** `append`
**Pass judgment:** `approved`

### Findings

No findings. Exact compatibility skill identifiers resolve against their generated or declared legacy
inventories, generated hook identity is independent of cache layout, repository-wide marker detection is
bounded through Git's quiet search, and case-insensitive pathspec behavior is proven by a real Git-backed
test.

Verification on the frozen tree: 62 generated files current, route self-test passed, 12 hook tests passed,
and 9 marketplace/contract tests passed (the pinned external-source case remains CI-owned).

## Review pass — 2026-09-13 — final aggregate

**Candidate base:** `f08caa4396ffc51cc9d9a9d21d419d225f8bdaf3`
**Candidate head:** `7cb9d9e589ac819561bb530eb8fb3d9a4ea6c1c3`
**Candidate branch:** `Feature/Layered-Cpp-Marketplace`
**Candidate scope:** `all`
**Candidate path-set:** `sha256:6d1f9cf3cc00b763e09084e1b7a4b5c388b5d38a1a941e923f20a9399da36d6c` `(87 paths)`
**Candidate bundle:** `C:\Users\tommy\source\repos\cpp\windows\cpp-agents\.git\agent-workflow\runs\cpp-marketplace-migration\review\61b2994ac07d9e9a713e57f667a2c31da3bdde342112bb9792befa0f0fe9ca88`
**Candidate bundle identity:** `sha256:1ae8d693d260884deafc5c2bbc3ed1f1d41a8c68a8459b015c6ee7ae74f5b696`
**Work-order path:** `reviews/Feature-Layered-Cpp-Marketplace.md`
**Work-order mode:** `append`
**Pass judgment:** `changes-requested`

### Findings

- [x] **R15 — MEDIUM — case-insensitive write-time routes** —
  `.agents/gen_skill_routes.py:11`
  Session detection recognizes uppercase C++ suffixes, but generated route regexes and the self-test matcher
  are case-sensitive, so `MAIN.CPP` receives no write-time skills. Make source/resource extension routes
  case-insensitive and add uppercase routing assertions.
  Fixed in the next remediation commit: source, test, build, and Windows-resource regexes use scoped
  case-insensitive groups, with explicit `MAIN.CPP` and `APP.RC` route assertions.

- [x] **R16 — MEDIUM — canonical hook identity classification** — `MIGRATION.md:16`,
  `.agents/hooks/session_context.py:22`
  The migration classifies old names in canonical hooks as errors, while the shared source and generated
  `base` hook contain an unreachable legacy branch. Generate package-specific messages from canonical hook
  data so `base` contains only canonical identities and the compatibility payload alone receives rewrites.
  Fixed in the next remediation commit: the authored hook contains canonical messages only, compatibility
  generation rewrites that body, and validation rejects retired identifiers in both authored and generated
  base hooks.

Validation on the frozen aggregate candidate: 62 generated files current, route self-test, 12 hook tests,
9 contract tests, all five Codex validators, and strict Claude marketplace plus plugin validation passed.
Those gates did not assert uppercase write routes or require the canonical hook payload to be free of retired
identities.
