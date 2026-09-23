# C++ design standards and canonical skill names

## Objective

Publish one reusable, idiomatic C++ design standard derived from established DDD vocabulary,
the C++ Core Guidelines, and explicit state/logic separation, then apply its decisions to the
Sandbox HWID lab as a foundation for a growing, multi-feature system. Current code size is
not a reason to flatten ownership or postpone useful module boundaries. Separate scalable
architecture from inventing domain invariants that the present wire records do not have.

## Authorization

Tommy authorized completing the research and reusable agent guidance, correcting redundant
skill names, and applying the resulting design to the current lab. Driver installation,
loading, signing-policy changes, VM operations, and unrelated WinWrap implementation remain
outside this work.

Completed steering (2026-09-23): Tommy authorized updating existing cpp-agents PR #13 and the
Sandbox HWID application to use type-owned static request validation and the identity
feature namespace. Retain and explain the ABI assertions. This turn updates the review
candidate and sandbox; it does not claim or require a merge, publish a release, or expand
driver/runtime scope. The earlier Claude handoff produced the commits recorded below.

Completed namespace steering (2026-09-23): apply a project/library namespace by default and add nested
namespaces for meaningful subsystem or contract boundaries. Keep `Identity` and
`IdentityRequest`; use `sandbox_hwid::protocol` for the shared client/driver wire contract.
Keep namespace depth independent of folders and architectural scale. A useful library
boundary does not require a second consumer. Update the existing guidance and sandbox PRs;
no wider product-tree reorganization was selected. Keep process notes brief.

Latest steering (2026-09-23): put response rules and their typed errors with `Identity`,
leaving byte-length checking, copying and delegation in the client decoder. Apply this
ownership rule to the reusable standards as well as the sandbox and update the existing PRs.

## Settled decisions

- Canonical skill identifiers use the plugin as the namespace and a non-redundant capability
  name: `cpp:style`, `cpp:build`, `gpp:toolchain`, `msvc:toolchain`, and `win32:style`.
- Existing redundant identifiers remain only as time-bounded compatibility aliases where the
  published compatibility window requires them.
- The reusable design capability is `cpp:domain-design`.
- DDD supplies modelling vocabulary and boundaries; it does not require inheritance-heavy OOP,
  a `domain` namespace/folder, or a class for every data type.
- Use a `struct` for passive data whose members may vary independently. Use a `class` when a
  real invariant requires controlled construction or representation.
- A fallible factory such as `create` establishes a valid value. Member functions represent
  operations on an encapsulated value. Prefer a static member such as `IdentityRequest::validate`
  for a stateless check owned by that one type when grouping makes the API clearer. Associated
  free functions remain appropriate for independent algorithms and boundary adapters. This
  grouping preference is a house decision, not a requirement of C.4/C.5 or DDD.
- Types own their validation rules and typed errors. Representation adapters check framing,
  copy or convert input, then delegate without duplicating those rules. Keep client-only
  dependencies outside the shared C++17 contract; an intrinsic representation may still
  justify a type-owned parsing factory when its dependencies fit that component.
- Immutable transformations use a domain-specific verb. `with_x` is available when it truly
  means "copy this value with one replacement" but is not a mandated C++ naming pattern.
- C++ value semantics do not require an immutable API. Prefer immutable domain values when
  that simplifies reasoning; preserve efficient local mutation and invariant-preserving
  member operations where appropriate. A fallible factory is useful for expected invalid
  input, not a mandatory substitute for every constructor.
- Keep mutable state and external I/O in coarse boundary components; keep core transformations
  explicit and independently testable.
- Sandbox HWID currently has passive wire records, not a behaviour-bearing domain model.
  Their struct representation, validation semantics and ABI checks remain appropriate within
  a scalable architecture. Preserve the names `Identity` and `IdentityRequest`. The published
  contract namespace is `sandbox_hwid::protocol`; it names the shared wire boundary
  without imposing a namespace on every feature or folder. Ordinary static functions do not alter object layout.

## Work

### 1. Reusable cpp-agents source

- [x] Perform an independent research pass before authoring: use primary or authoritative
      sources for DDD vocabulary, C++ Core Guidelines, modern C++ value-oriented design,
      state/effect separation, naming, and representative production-library practice.
      Distinguish sourced conventions from deliberate house decisions, challenge the settled
      draft where evidence disagrees, and retain concise source rationale for the final report.
- [x] Rename canonical authored skill capabilities to remove duplicated scope words.
- [x] Preserve the documented compatibility packages and their old identifiers through the
      existing 2027-03-31 window.
- [x] Add `cpp:domain-design` with generic examples covering passive records, invariant-bearing
      values, fallible factories, immutable transformations, associated free functions,
      stateful adapters, entities/value objects, typed errors, and namespace ownership.
- [x] Update routes, manifests, source/package mappings, documentation, hooks, tests, and
      generated outputs from their canonical owners.
- [x] Validate generator freshness, route self-tests, hooks, package contracts, host validators,
      and scaffold acceptance checks required by `AGENTS.md`.

### 2. Sandbox HWID application

- [x] Update the lab to the canonical installed skill identifiers after the reusable package is
      available.
- [x] Apply role-based protocol naming: `IdentityRequest`, `IdentityRequestError`,
      `IdentityError`, and `query_identity` (the original free validator is superseded below).
- [x] Keep `Identity` as a passive ABI record and record why a separate domain model is
      not currently justified.
- [x] Preserve the client/kernel ABI and all explicit host-versus-VM safety boundaries.
- [x] Run the authorized host build, tests, formatting, static analysis, and real WDK build as
      applicable; do not install or load the driver.

### 3. Function ownership and feature namespace correction (2026-09-23)

- [x] Correct canonical domain-design/style guidance, regenerate packages, and validate.
- [x] Move sandbox request validation to `IdentityRequest::validate` and use
      `sandbox_hwid::identity` consistently in namespaces, headers, consumers and current docs.
- [x] Preserve ABI assertions and validate standard-layout, aggregate and trivial-copy traits;
      rerun the real client/tests and C++17 WDK build/analysis.
- [x] Commit the bounded corrections, update existing cpp-agents PR #13, and publish a
      reviewable sandbox companion candidate without staging unrelated work.

### 4. Namespace and scalable module correction (2026-09-23)

- [x] Preserve `Identity` and `IdentityRequest`; remove the automatic feature-namespace rule.
- [x] Use `sandbox_hwid::protocol` for the shared wire contract and its decoder; update
      public include paths, consumers, WDK project references and current conventions.
- [x] Clarify that namespace hierarchy need not mirror folders, and that one consumer is
      sufficient for a useful library API, dependency boundary or independent testing.
- [x] Regenerate packages, validate the required source/host checks and rebuild the sandbox.

The existing client, driver and shared roots retain their ownership. The shared ABI remains
C++17 without user-mode dependencies; the client decoder remains C++23. Type-owned static
validation and all size/offset checks stay in place. No new domain model or operation names
are needed for this correction.

### 5. Response validation ownership (2026-09-23)

- [x] Document type-owned rules/errors and representation-adapter delegation in the canonical
      design skill, then regenerate its packages.
- [x] Move response field checks and `IdentityError` into the shared identity header; make
      the C++23 decoder check length, copy, delegate and propagate the same error categories.
- [x] Complete host validation, update current documentation and refresh the lab's guidance.
- [x] Commit and update source PR #13 and sandbox draft PR #1, preserving unrelated work.

## Acceptance criteria

- Canonical examples read as ordinary modern C++, not translated C# or a prescribed OO style.
- No canonical identifier repeats its namespace (`cpp:cpp-*`, `gpp:gpp-*`, and equivalent
  forms are absent outside compatibility fixtures/documentation).
- Compatibility consumers continue resolving their published old identifiers.
- Generated packages and routes are reproducible and all required repository checks pass.
- The lab builds and its host tests pass with unchanged wire layout and no driver execution.
- The final explanation includes generic examples plus the concrete Sandbox HWID mapping.

## Progress

- 2026-09-23 response ownership delivered to [source PR #13](https://github.com/tj-agents/cpp/pull/13)
  and [sandbox draft PR #1](https://github.com/tomjseery/sandbox-hwid/pull/1). Published code
  commits are `73c039cd86299a825ab9f68f56eb11af7234ec05` and
  `977798dd4a45e39b250be0ec53ceb21b90e0a7bd`; remote heads were verified. This plan checkpoint
  follows the source code commit. Unrelated sandbox edits remain local. Neither PR is merged;
  the existing trusted-provenance prerequisite remains with the debt owner below.
- 2026-09-23 response ownership implemented and validated. Required generator/routes, 11 hook
  tests and 51 source tests pass (one existing optional skip). Both hosts accept all nine
  packages; evidence is in `C:\Users\tommy\AppData\Local\Temp\cpp-rules-hosts-fc59do6c`.
  Sandbox client/9 tests, real WDK rebuild/analysis, direct C++17 `/kernel` constexpr checks,
  owned formatting and client clang-tidy pass. Current docs and local cpp guidance are updated.
  MSVC 19.51 rejects valid constexpr reads of implicit zero padding after string literals;
  an isolated reproduction confirms this is independent of validation. Compile-time test
  fixtures now use explicit character initializers; production records are unchanged.
- 2026-09-23 namespace correction implemented and validated for the existing PRs. The shared
  contract uses `protocol`; the type names and ABI remain unchanged. Source generator/routes,
  11 hook tests and 51 source tests pass (one existing optional skip); both hosts accept all
  nine packages. The C++17 guide example compiles. Sandbox client/8 tests, real WDK build and
  analysis, formatting of owned changes, and client clang-tidy pass. Local cpp/msvc guidance
  was refreshed and byte-verified. The prior candidate SHAs below remain historical evidence.
- 2026-09-23 requested correction delivered for review. Source PR
  https://github.com/tomjseery/cpp-agents/pull/13 is updated at
  `45c448cdf3a9f653a9b9348502b0513e06b3f4fe`; the sandbox companion draft is
  https://github.com/tomjseery/sandbox-hwid/pull/1 at
  `52e8632fc002111145501859e9d52c4c00cad170`. Both remote branch SHAs were verified after
  pushing, and the existing source PR description was rewritten for the final change.
  Generated-package CI and Ubuntu/Windows attester-safety jobs pass on that source head;
  repository-binding still fails at the documented provenance gate. Neither PR is merged.
  The source workspace's final plan checkpoint is local bookkeeping after the published
  candidate; it does not change the validated source or require another CI-triggering push.
- 2026-09-23 correction validation: all required source checks pass. Generator is current at
  220 files / 16 definitions; six route profiles pass; 11 hook tests and 51 source tests
  pass with one existing optional live-source skip (61 executed passes total). This includes
  marketplace, attester, generator safety and both scaffold suites. Claude strictly validates
  the marketplace and nine packages; Codex installs all nine into an isolated profile.
  Host evidence: `C:\Users\tommy\AppData\Local\Temp\cpp-identity-host-validation-dlisbfjd`.
  The new C++17 example compiles with G++ `-Wall -Wextra -Werror -pedantic`; constexpr
  validation and standard-layout/trivial-copy/aggregate assertions pass.
- 2026-09-23 sandbox correction: client build and all 8 CTests pass; WDK C++17 `/kernel`
  build and `/analyze` rebuild each have zero warnings/errors. All seven C++ files pass
  clang-format and both client translation units pass clang-tidy with no owned diagnostics.
  All original data fields, field order, GUID and IOCTL compare unchanged; sizes, every
  metadata offset and the original text offsets are asserted. Host trait checks cover both
  records. Client help succeeds; driver is `NotSigned`. Current logs and hashes are recorded
  in the sandbox verification document. No driver/runtime actions occurred.
- 2026-09-23 local capability refresh: reinstalled only the already-selected `cpp` 0.2.0
  through Codex's supported installer in the sandbox directory; installed style/design
  bytes match generated source and the global marketplace registration is unchanged.
- 2026-09-23 provenance diagnosis: the earlier migration changed two blobs pinned by the
  trusted attester on `main` (marketplace tests and CI). Missing attestation is therefore
  not resolved by simply rerunning the old script. The separate reviewed trust-pin update
  and objective completion condition are owned by
  [the provenance debt entry](../../TECH_DEBT.md#review-provenance-pins-for-the-canonical-capability-migration).
  Preserve this gate when updating PR #13; do not weaken it or post an unverified success.
- 2026-09-23 correction resumed by the current Codex session at Tommy's request. The source
  checkout is clean at `f2f4ecd1082a2e7d7f71ac1e9abed062942ebb15`; PR #13 is open at that
  exact head: https://github.com/tomjseery/cpp-agents/pull/13. Its generated/attester tests
  passed, but the repository-binding provenance check failed; inspect and resolve or report
  the actual remaining gate when updating the candidate. No merge has occurred.
- 2026-09-23 sandbox HEAD is `881769bc37f03af32cd18d4a74bcc644c17abee5` on
  `Refactor/Canonical-Structure`, with no open PR. Preserve unrelated dirty
  `docs/next-session.md`, `docs/winwrap-integration.md`, `.codex/`, both handoff prompt files,
  and `nvim.log`. This correction owns only the relevant source/header moves, consumers,
  ABI checks, build header paths and current design/verification documentation.
- 2026-09-22 handoff checkpoint: Source checkout remains
  `C:\Users\tommy\AppData\Local\Temp\cpp-agents-explicit-wire-types`, branch
  `fix/explicit-wire-integer-types`, HEAD `e0304dfcba2db5263eb9822e2b06e6706f311165`.
  All design/migration edits described above remain uncommitted. A fresh GitHub query
  for every PR state on this head branch returned `[]`; no PR for this branch was found.
  This session has not published or merged these changes. The source retains the earlier
  exact-width conventions commit, which must not be lost.
- 2026-09-22 handoff checkpoint: The lab remains
  `C:\Users\tommy\source\repos\sandbox-hwid`, branch `Refactor/Canonical-Structure`,
  HEAD `03a2ffef8640508c2bf664802507030c3571141c`. Its design application is already
  implemented and validated locally. The latest chat showed the scheduling examples from
  the skill plus a mutable `Appointment` example to explain entities. Those teaching
  examples are not a proposal to add appointments, entities, factories, or a domain layer
  to the HWID protocol.

## Earlier Claude transfer

- Transfer requested by Tommy; target harness is Claude Code with its configured default
  model. The earlier `gpt-6-astra` selection concerned the independent Codex research pass;
  it does not override this newer explicit Claude request.
- Launch directory is the source checkout above. Prompt file is
  `C:\Users\tommy\AppData\Local\Temp\cpp-design-claude-handoff.txt`.
- The parent submitted one packaged `machine:handoff-claude` launch and released writing
  ownership on its success message. The resulting commits and PR are observed above.
  The current user request returns ownership of the bounded correction to this Codex session;
  do not launch another owner for it.
- Preserve pre-existing lab changes in `docs/next-session.md`, `docs/winwrap-integration.md`,
  `.codex/agents/`, both `BASE_AGENTS_*PROMPT.md` files, and `nvim.log`. Do not stage them
  accidentally with this work. The unrelated temporary patch seen earlier is absent from
  the latest status; this session did not remove it.
- This task owns the lab's `.agents/skill-routes.json`, `AGENTS.md`, `README.md`,
  `shared/include/sandbox_hwid/protocol/identity.hpp`,
  `client/include/sandbox_hwid/protocol/validation.hpp`, `client/src/validation.cpp`,
  `client/src/main.cpp`, `driver/driver.cpp`, `tests/validation_test.cpp`,
  `docs/conventions.md`, `docs/verification.md`, and the newly added `.codex/config.toml`.
  The latter is machine-local; preserve existing agent files and do not publish its
  absolute temporary source path as a portable project setting.

## Earlier execution evidence

- 2026-09-22: Implementation and local delivery completed. Independent generator review found
  no lost published skill paths, unresolved package references, or resource-link failures.
  Final required PowerShell generator check reports 220 current files / 16 definitions.
  Claude Code 2.1.278 strictly validated the marketplace and all nine packages. Codex CLI
  0.155.1 installed all nine into an isolated profile. Final G++ scaffold matrix passed
  all five tests, including actual C++20/23 builds; MSVC matrix passed all three tests.
  All eight Python suites passed: 61 tests passed, one pre-existing optional live-source
  comparison skipped. Historical signed provenance is unchanged and its pinned checks passed.
- 2026-09-22: Sandbox HWID renames and design rationale completed. Client build and 8/8
  tests pass; real WDK 10.0.28000.0/KMDF 1.31 build and `/analyze` rebuild have zero warnings
  or errors; clang-format checks all seven C++ files and clang-tidy checks both client
  translation units. Request/response sizes stay 16/160 bytes with text offsets 16/64/112.
  ABI declarations, error mappings, protocol version, GUID and IOCTL are unchanged.
  Detailed logs and artifact hashes are recorded in the lab's `docs/verification.md`.
- 2026-09-22: Initial global per-command local installs byte-verified at 0.2.0, but the
  shared cache later contained 0.1.0 again. Diagnosed the effective source selection and
  added a lab-only `.codex/config.toml` local marketplace setting. Ordinary lab-directory
  install and subsequent list commands, with no source overrides, now resolve `cpp`,
  `msvc`, and `win32` 0.2.0 and installed payload bytes match. The global Git source and
  revision are unchanged; legacy cpp-agents plugins are disabled only in the lab profile.
  Existing `.codex/agents` and unrelated dirty files were preserved. A concurrently appearing
  `.tmp-model-routing-debt.patch` was left untouched.
- 2026-09-22: Delivery is local source, generated packages, installed lab selection, and
  validated lab code. No remote publication or Git commit was performed. The lab's local
  source setting depends on this checkout remaining available until the release is published;
  its removal and revalidation procedure is documented in `docs/conventions.md`.
  No driver loading, installation, signing-policy change, VM operation, or WinWrap change
  was performed. Guest/runtime and fresh INF/CAT evidence remain outside this task.
- 2026-09-22: Independent research completed against the C++ Core Guidelines (C.2/C.4/C.5,
  construction, F.8, NL.8), Evans' DDD Reference, Abseil factory guidance, WG21 P0323R12,
  Sean Parent's value-semantics material, Gary Bernhardt's functional-core/imperative-shell
  explanation, and Boost.URL's production API. Primary-source links and concise rationale
  live in the canonical `domain-design/SKILL.md`. The earlier Brian Will reference was not
  needed as independent evidence. Review clarified that Evans recommends immutable DDD
  Value Objects; allowing mutable C++ values is an explicit broader house adaptation.
- 2026-09-22: All 15 existing capabilities renamed; `cpp:domain-design` added. Canonical
  packages are 0.2.0; legacy packages received patch increments. Generator now resolves
  qualified source identities and produces 220 files from 16 definitions. Canonical old
  names redirect locally until 2027-03-31; compatibility packages retain old names.
  Fixed the discovered G++ packaged script-link relocation alongside the MSVC mapping.
- 2026-09-22: Observed green checks so far: generator safety 17/17; marketplace 15 passed
  with one optional live-source comparison skipped (pinned signed verification passed);
  attester 4/4; hooks 11/11; route/structure 6/6; route self-test across six profiles;
  MSVC scaffold acceptance 3/3. Some process launches required sandbox escalation.
  G++ scaffold validation and strict Claude validation are still running. Codex installed
  all nine packages successfully into the isolated temporary validation profile.
- 2026-09-22: Extracted the complete C++23 example from the skill and compiled it with
  G++ using `-Wall -Wextra -Werror -pedantic`; runtime checks passed for valid/invalid
  construction, preserved input, overlap, and extreme integer shifts. Independent review
  found no example correctness issue. A separate generator review is in progress.
- 2026-09-22: Sandbox HWID application started after local package generation and checks.
  The existing dirty files remain outside the edit lease. Parent owns only lab guidance
  and route migration; worker owns protocol/client/kernel naming, relevant docs, and host
  validation. No driver execution or VM operation is authorized.
- 2026-09-22: Resumed in the requested cpp-agents checkout with `engineering:plan-execution`
  in its runtime-unavailable mode. Existing branch is `fix/explicit-wire-integer-types`;
  the pre-existing commit and Sandbox HWID's unrelated dirty files are preserved.
  Independent source review is in progress. Generator migration uses qualified source
  identities, explicit flat host-adapter names, and generated dated compatibility aliases.
  Research and authored guidance remain with the parent; independent workers own generator
  compatibility, routes/tests, and read-only Sandbox HWID evidence.
- 2026-09-22: Research reconciled against Eric Evans' DDD reference, Brian Will's procedural
  programming/state guidance, and C++ Core Guidelines C.1-C.5. Existing cpp-agents source and
  Sandbox HWID identity flow inspected. No deliverable edits or runtime actions performed yet.
- 2026-09-22: The first default-model handoff was launched and then stopped by Tommy before
  implementation. Tommy explicitly selected `gpt-6-astra` for a stronger independent research
  pass; the replacement handoff must use that model rather than inheriting the CLI default.

## Next Steps

The response-validation implementation, reusable guidance, host checks and existing PR updates
are complete. Local cpp guidance is refreshed. The release prerequisites remain:

1. Before merging source PR #13, resolve the separately reviewed provenance-pin update and
   trusted exact-head attestation described in the linked debt owner. Preserve the signed
   archive and the gate. This correction did not authorize bypassing that review requirement.
2. Review sandbox draft PR #1 against the completed host evidence; retain the unrelated local
   teaching notes and agent configuration outside it. Driver/VM work remains out of scope.
3. After a separately authorized merge makes the release available, refresh installed packages,
   remove only the lab-local marketplace source override, and reverify all nine routed skill
   identifiers from the published source. Retain the source checkout while that override is
   needed. This remains a release follow-up, not evidence that PR #13 is already merged.
