# Changelog

## v0.4.2 — standalone mixin capability

Packages: `cpp@0.4.2`; compatibility `base@0.7.2`, `cpp-standards@0.7.2`.

- Moved all mixin, CRTP behavior-provider, layout, macro-containment, and composition-test
  guidance into the standalone `cpp:mixins` capability.
- Removed mixin ownership from `cpp:domain-design`, `cpp:structure`, `cpp:style`, and
  `cpp:testing`; domain design remains limited to its declared modelling concerns.
- Added an authored capability-ownership rule plus regression coverage preventing general
  C++ patterns from being filed under an unrelated skill again.

## v0.4.1 — mixin composition and header exposure guidance

Packages: `cpp@0.4.1`; compatibility `base@0.7.1`, `cpp-standards@0.7.1`.

- Added generic mixin guidance for behavior-oriented naming, stateless `struct` providers,
  stateful invariant-bearing `class` providers, and explicit first-match routing policy.
- Documented composition hazards including overlapping conditions, hidden order, shared
  state, lifetime coupling, and resource-owning base construction/destruction.
- Clarified that source and public-header layout follows domains, resources, and stable
  protocols rather than C++ mechanisms, and that `detail/` marks an unsupported
  compatibility contract rather than access control.
- Added library-prefixed macro containment, deliberately repeatable internal fragments,
  independent public-header leakage checks, and behavior-focused composition tests.

## v0.3.0 — workspace scaffold reconciliation

Packages: `cpp@0.3.0`, `gpp@0.3.0`, `msvc@0.3.0`, `win32@0.3.0`; compatibility
`base@0.6.0`, `cpp-standards@0.6.0`, `gcc@0.5.0`, `gpp-standards@0.5.0`, `windows@0.8.0`.

Reconciles the reusable behaviour of the older `tomjseery/cpp` workspace's `newcpp`
scaffold into the canonical packages.

- Added `win32:scaffold`, a toolchain-independent overlay that converts a fresh G++ or MSVC
  scaffold into a Unicode Win32 GUI application (`wWinMain`, embedded Per-Monitor V2 /
  Common Controls v6 / UTF-8 / `asInvoker` manifest, Win32 clang-tidy carve-outs and
  `<windows.h>` include ordering). A customized configuration or route profile is left
  untouched and reported. Legacy `windows` carries it as `win32-scaffold`.
- Both scaffolds now share one `cpp`-owned template set: canonical `.clang-format`,
  `.clang-tidy` (including `-portability-avoid-pragma-once` and pointer conditions),
  `.editorconfig`, clangd VS Code settings, `AGENTS.md`/`CLAUDE.md`, and the shared
  `libs/core`/`app`/`tests` sources. MSVC projects receive the canonical formatter and
  analysis configuration unless `-FormatConfig`/`-TidyConfig` override it.
- Sanitizers are target-scoped `<project>_sanitize` carriers in both toolchains instead of
  global flags. G++ gains a `gdb` preset; MSVC gains an `asan` preset; `Build.ps1 -Configuration Asan` selects an
  installation with the AddressSanitizer component and configuration fails clearly without it.
  MSVC warnings-as-errors is now target-scoped too, and the developer shell puts a native
  Windows CMake ahead of MSYS2/MinGW builds.
- Generated projects carry the route profile for their exact composition, rendered by the
  route generator; module scanning is off until a project adopts modules, so clangd and
  clang-tidy parse the compile database; debugger launch configurations and an on-`PATH`
  install rule are included.
- `msvc:toolchain` records its skill-tree picks; learning and structure guidance name the
  canonical scaffolds instead of the workspace `newcpp` command.
- Package content changes now require a new version: `.agents/plugins/package-versions.json`
  records every version's content digest and the tests enforce it.

## v0.2.0 — canonical capability names and domain design (2026-09-23)

Packages: `cpp@0.2.0`, `gpp@0.2.0`, `msvc@0.2.0`, `win32@0.2.0`; compatibility
`base@0.5.0`, `cpp-standards@0.5.0`, `gcc@0.4.2`, `gpp-standards@0.4.2`, `windows@0.7.0`.

- Added `cpp:domain-design` with researched modelling guidance and a complete C++23 example.
- Clarified type-owned static validation, namespaces for actual ownership boundaries, and
  retaining binary layout assertions independently of domain modelling; included a C++17
  record example with meaningful domain names.
- Made type-owned rules and errors explicit: representation decoders check/copy input
  and delegate to the owner without importing client-only dependencies into shared types.
- Allowed cohesive library targets for dependency control and testing with one consumer;
  separated namespace depth from folder structure and architectural scale.
- Shortened canonical capability names, including `cpp:style`, `gpp:toolchain`,
  `msvc:scaffold`, and `win32:style`; retained old identifiers through 2027-03-31.
- Made source discovery scope-aware and flat host-adapter names explicit, preserving the
  combined legacy Windows package and historical signed provenance.
- Updated technical routes and session guidance to use canonical identifiers.
- Compatibility packages translate every canonical identifier, including cross-scope
  references, into their legacy namespace, and carry new versions for changed content.
- Every host manifest names the canonical `tj-agents/cpp` repository.

## 0.3.0 — layered marketplace migration

- Introduced the public `base`, `windows`, and `gcc` plugins.
- Migrated native Windows standards from windows-agents into cpp-agents.
- Renamed routes to `base:*`, `windows:*`, `gcc:*`, and canonical `concertable:*` workflow skills.
- Added explicit dependencies, compatibility metadata, signed external skill-contract provenance, and layered detection tests.
- Retained generated `cpp-standards` and `gpp-standards` aliases through 2027-03-31.
- Archived `windows-agents` after every known consumer migrated, leaving `cpp-agents` as the only active C++ standards marketplace.
