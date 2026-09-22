# C++ design standards and canonical skill names

## Objective

Publish one reusable, idiomatic C++ design standard derived from established DDD vocabulary,
the C++ Core Guidelines, and explicit state/logic separation, then apply its decisions to the
Sandbox HWID lab without forcing a domain layer that the lab does not need.

## Authorization

Tommy authorized completing the research and reusable agent guidance, correcting redundant
skill names, and applying the resulting design to the current lab. Driver installation,
loading, signing-policy changes, VM operations, and unrelated WinWrap implementation remain
outside this work.

Latest steering: Tommy asked whether the existing Sandbox HWID should use the new design,
provided the reusable guidance has merged, then explicitly requested a Claude handoff.
The merge is a prerequisite to check, not an observed fact. Carry the existing authorized
work into Claude, establish the reusable delivery state, and reconcile the lab against the
guidance. Do not interpret the question as a request to manufacture new domain entities or
expand the driver/runtime scope.

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
  genuine operations on one encapsulated value. Stateless operations that do not need private
  representation are free functions in the associated namespace.
- Immutable transformations use a domain-specific verb. `with_x` is available when it truly
  means "copy this value with one replacement" but is not a mandated C++ naming pattern.
- C++ value semantics do not require an immutable API. Prefer immutable domain values when
  that simplifies reasoning; preserve efficient local mutation and invariant-preserving
  member operations where appropriate. A fallible factory is useful for expected invalid
  input, not a mandatory substitute for every constructor.
- Keep mutable state and external I/O in coarse boundary components; keep core transformations
  explicit and independently testable.
- Sandbox HWID currently has passive protocol records, not a behaviour-bearing domain model.
  Its protocol types remain `struct`s under `sandbox_hwid::protocol`; no synthetic `domain`
  layer or immutable-update methods will be introduced.

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
      stateful adapters, entities/value objects, typed errors, and feature-oriented namespaces.
- [x] Update routes, manifests, source/package mappings, documentation, hooks, tests, and
      generated outputs from their canonical owners.
- [x] Validate generator freshness, route self-tests, hooks, package contracts, host validators,
      and scaffold acceptance checks required by `AGENTS.md`.

### 2. Sandbox HWID application

- [x] Update the lab to the canonical installed skill identifiers after the reusable package is
      available.
- [x] Apply role-based protocol naming: `IdentityRequest`, `IdentityRequestError`,
      `validate_request`, `IdentityError`, and `query_identity`.
- [x] Keep `protocol::Identity` as a passive ABI record and record why a separate domain model is
      not currently justified.
- [x] Preserve the client/kernel ABI and all explicit host-versus-VM safety boundaries.
- [x] Run the authorized host build, tests, formatting, static analysis, and real WDK build as
      applicable; do not install or load the driver.

## Acceptance criteria

- Canonical examples read as ordinary modern C++, not translated C# or a prescribed OO style.
- No canonical identifier repeats its namespace (`cpp:cpp-*`, `gpp:gpp-*`, and equivalent
  forms are absent outside compatibility fixtures/documentation).
- Compatibility consumers continue resolving their published old identifiers.
- Generated packages and routes are reproducible and all required repository checks pass.
- The lab builds and its host tests pass with unchanged wire layout and no driver execution.
- The final explanation includes generic examples plus the concrete Sandbox HWID mapping.

## Progress

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

## Claude transfer ownership

- Transfer requested by Tommy; target harness is Claude Code with its configured default
  model. The earlier `gpt-6-astra` selection concerned the independent Codex research pass;
  it does not override this newer explicit Claude request.
- Launch directory is the source checkout above. Prompt file is
  `C:\Users\tommy\AppData\Local\Temp\cpp-design-claude-handoff.txt`.
- The parent will submit exactly one packaged `machine:handoff-claude` launch and release
  writing ownership on its success message. Launcher success proves submission, not that
  Claude has read this file. Claude should acknowledge ownership here before edits.
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

Continue the same goal in Claude: establish whether the reusable guidance is actually merged,
prepare its remaining delivery work, and reconcile the already-updated lab with the available
release. The research and local implementation are finished; do not restart them.

1. Read the source checkout's README and AGENTS, then the canonical
   `.agents/base/contract/domain-design/SKILL.md` and this checkpoint. Confirm both Git
   identities and preserve all described dirty work. Acknowledge transfer ownership here.
2. Inspect current remote/default-branch and PR state. The latest check found no PR on
   `fix/explicit-wire-integer-types`, and these edits are still uncommitted. Prepare the
   reusable changes for review and normal authorized repository delivery; follow applicable
   delivery rules and retain real approval gates. Local installation is not merge evidence.
   Preserve the 2027-03-31 compatibility window and historical signed provenance.
3. Review the existing lab application against the new guidance. Its current correct shape
   is passive protocol structs plus free validation and boundary I/O, with the five recorded
   role-based names. Add encapsulated values/entities only if actual new domain invariants
   justify them; Tommy's request does not supply any such new requirements.
4. Once the validated release is actually available from the Git marketplace, refresh the
   canonical packages for the consuming host, remove only the lab-local marketplace source
   override, and verify that all nine routed skill identifiers resolve from that published
   release. Keep the source checkout while the local override is needed. Record concrete
   merge/release/install evidence and update the lab's current provenance paragraph.
5. Preserve the completed host checks as evidence. Rerun required source checks for the final
   delivery candidate and rerun affected lab build/test/format/analysis checks if changes
   warrant it. Keep the same plan current through delivery. Driver installation/loading,
   signing-policy changes, VM work, and unrelated WinWrap changes remain unauthorized.
