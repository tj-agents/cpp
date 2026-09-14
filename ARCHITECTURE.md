# C++ standards delivery architecture

## One marketplace, three composable layers

```text
generic C++ repository        -> base
native Windows C++ repository -> base + windows
GCC/Linux C++ repository      -> base + gcc
cross-toolchain repository    -> base + windows + gcc when both genuinely apply
```

`base`, `windows`, and `gcc` are technical-standard layers in `tomjseery/cpp-agents`. `concertable@agent-standards` remains separate because it owns process: planning, review, testing workflow, delivery, repository management, and the shared write-time router.

## Ownership boundaries

- `standards/cpp/` owns only platform-neutral C++ rules.
- `standards/windows/` owns Win32, Unicode, MSVC/clang-cl, WIL, native-resource lifetime, Windows CMake, and Windows learning guidance.
- `standards/gcc/` owns GCC, g++, GDB, and Linux-specific guidance.
- Workflow/process identifiers refer to `concertable:*`; cpp-agents does not copy those rules.

A rule has one authored home. Router skills each own one document. Self-contained plugin payloads and temporary compatibility aliases are generated copies, checked for drift, rather than additional authored sources.

## Source-to-package flow

`.agents/plugins/marketplace.json` is the canonical Codex marketplace. `.agents/plugins/payloads.json` declares public plugins, payload domains, dependencies, hook owners, compatibility aliases, skill-name aliases, and removal dates. `.agents/plugins/skill-contract.json` pins external workflow skills that generated routes may reference. `contracts/` carries non-executable, signed Git provenance for that external contract so ordinary CI can verify the pinned content without duplicating its workflow standards. A trusted default-branch status gate then binds protected consumer heads to an authenticated check of the private producer repository without storing a cross-repository credential; its trust boundary and recovery contract are in `PROVENANCE_GATE.md`.

`.agents/sync-generated.ps1` validates those contracts and generates the local Claude skills, self-contained plugin payloads, the plugin-owned detection hook, Claude manifests and marketplace, and one topic index per standards domain.

The compatibility aliases may duplicate generated delivery payloads temporarily, but never own rule text. They are removed after 2027-03-31.

## Detection and routing

The session hook and route generator share canonical kinds: `generic`, `windows`, and `gcc`. They accept legacy `portable` and `gpp` kind values only as input compatibility and normalize them immediately.

An explicit route kind wins over the host. Without one, tracked `.rc`/`.manifest` files or Win32/WIL source markers select Windows; a Linux host selects GCC; otherwise only the base applies. The generator emits canonical kinds and namespaces.

Every matching row fires. Source files receive `base:cpp-style`; build files receive `base:cpp-build` and `base:cpp-libraries`; tests add `base:cpp-testing`; platform rows add `windows:*` or `gcc:gcc-toolchain`; guidance and route-table files use `concertable:docs-and-debt` and `concertable:skill-routes`.

## Compatibility boundary

The supported plugin schemas do not provide one portable cross-harness dependency or rename-alias field. cpp-agents therefore validates dependencies in source metadata and provides generated compatibility packages plus an explicit uninstall/reinstall procedure. See [MIGRATION.md](MIGRATION.md).
