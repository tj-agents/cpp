# Changelog

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
