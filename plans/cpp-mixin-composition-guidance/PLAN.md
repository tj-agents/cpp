# C++ mixin composition guidance

## Objective

Turn the reusable lessons from the completed Winwrap structure review into generic,
platform-neutral C++ guidance. Extend the existing canonical owners rather than adding a
new capability or a `mixin` folder convention. Publish the regenerated `cpp` and
compatibility packages after review and the repository's full validation suite.

## Authorization and boundaries

Tommy authorized planning, implementation, validation, review, and delivery in
`tj-agents/cpp`. The work may update canonical guidance, tests, generated artifacts,
package manifests, and package-version records required by those changes. Winwrap,
drivers, and host-machine state are out of scope. The unrelated commit on
`Docs/Record-Layer-Inheritance-Debt` remains preserved on that branch.

## Ownership decisions

- `cpp:domain-design` owns mixin representation and composition: capability-oriented
  behavior, transparent stateless providers versus invariant-bearing state, routing
  precedence, overlapping conditions, ordering, lifetime coupling, and public behavior.
- `cpp:structure` owns organization and exposure: domain/resource/protocol grouping,
  public templates that include internal support, the unsupported meaning of `detail/`,
  and the independence of folders from namespaces.
- `cpp:style` owns semantic mixin names and preprocessor containment.
- `cpp:testing` owns independent public-header compile checks and behavior-focused
  composition tests.
- No new capability, architectural layer, namespace, public API, or folder exists merely
  to categorize the C++ composition mechanism.

## Work

- [x] Add small generic examples that distinguish capability names such as
      `FileDroppable` from observed messages and protocol roles with natural names.
- [x] Explain `struct` versus `class` for behavior providers without inferring either
      choice from inheritance.
- [x] Document domain/resource/protocol file organization, public/internal header
      exposure, `detail/`, and folder/namespace independence.
- [x] Add a contained, library-prefixed macro example with an optional repeatable
      internal fragment and a public-header leakage compile check.
- [x] Cover first-match routing, overlap, ordering, state/lifetime coupling, and tests
      that prove observable composed behavior.
- [x] Regenerate all derived adapters and packages from `.agents/`.
- [x] Bump both host manifests for every package whose generated content changes, then
      append the new immutable package-version records.
- [x] Run generator freshness, route self-test, hooks, marketplace, attester,
      package-version, host-validator, and G++/MSVC/Win32 scaffold acceptance checks.
- [ ] Create a focused commit, complete independent review and any repair cycle, then
      deliver the reviewed exact head through the repository's pull-request workflow.

## Acceptance criteria

- Each requested decision appears once under its existing canonical owner with concise,
  generic C++ examples and no Winwrap/Win32-specific API names.
- The macro example leaves no library macro defined after including the public header;
  the deliberately repeatable internal fragment remains identified as unsupported.
- Composition guidance explains ambiguous matches and precedence as API behavior and
  includes tests for dispatch, fallthrough, ordering, and coupled lifetime/state.
- Generated output is reproducible, every changed package has a new recorded version,
  and all repository-required checks pass or have an accurately recorded environmental
  result.
- Review findings are resolved and the delivered pull request reaches its authorized
  terminal state.

## Progress

- 2026-09-24: Read the external handoff, repository instructions, README, existing plans,
  and canonical `domain-design`, `structure`, `style`, and `testing` skills. The earlier
  C++ design plan is complete and does not own this continuation, so this file is the
  single active plan. Created `Docs/CppMixinCompositionGuidance` from `origin/main`; the
  unrelated debt commit remains on `Docs/Record-Layer-Inheritance-Debt`.
- 2026-09-24: Implemented the four owner-scoped guidance updates and a regression test
  covering canonical plus `cpp`, `base`, and `cpp-standards` generated packages. Bumped
  `cpp` to 0.4.0 and the two compatibility packages to 0.7.0 in both host manifests,
  regenerated 291 files from 17 definitions, and recorded final package digests.
- 2026-09-24: Local validation green: generator `-Check`; route self-test across six
  profiles; hook syntax plus 11 hook tests; 68 source tests with one expected optional
  skip, including marketplace, attester, package-version, and real G++/MSVC/Win32
  scaffold acceptance checks; strict Claude marketplace and all-nine-plugin validation.
  The installed Codex CLI has no read-only validation command, and its installer would
  modify forbidden host state, so the existing isolated CI install job owns that check.

## Next action

Create the focused-green commit, run independent review and any repair/incremental-review
cycle, then open and drive the pull request and exact-head CI to terminal delivery.
