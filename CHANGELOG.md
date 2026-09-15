# Changelog

## 0.3.0 — layered marketplace migration

- Introduced the public `base`, `windows`, and `gcc` plugins.
- Migrated native Windows standards from windows-agents into cpp-agents.
- Renamed routes to `base:*`, `windows:*`, `gcc:*`, and canonical `concertable:*` workflow skills.
- Added explicit dependencies, compatibility metadata, signed external skill-contract provenance, and layered detection tests.
- Retained generated `cpp-standards` and `gpp-standards` aliases through 2027-03-31.
- Archived `windows-agents` after every known consumer migrated, leaving `cpp-agents` as the only active C++ standards marketplace.
