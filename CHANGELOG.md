# Changelog

## Unreleased — canonical capability names and domain design

- Added `cpp:domain-design` with researched modelling guidance and a complete C++23 example.
- Shortened canonical capability names, including `cpp:style`, `gpp:toolchain`,
  `msvc:scaffold`, and `win32:style`; retained old identifiers through 2027-03-31.
- Made source discovery scope-aware and flat host-adapter names explicit, preserving the
  combined legacy Windows package and historical signed provenance.
- Updated technical routes and session guidance to use canonical identifiers.

## 0.3.0 — layered marketplace migration

- Introduced the public `base`, `windows`, and `gcc` plugins.
- Migrated native Windows standards from windows-agents into cpp-agents.
- Renamed routes to `base:*`, `windows:*`, `gcc:*`, and canonical `concertable:*` workflow skills.
- Added explicit dependencies, compatibility metadata, signed external skill-contract provenance, and layered detection tests.
- Retained generated `cpp-standards` and `gpp-standards` aliases through 2027-03-31.
- Archived `windows-agents` after every known consumer migrated, leaving `cpp-agents` as the only active C++ standards marketplace.
