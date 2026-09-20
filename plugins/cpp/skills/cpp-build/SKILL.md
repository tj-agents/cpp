---
name: cpp-build
description: Generic CMake target, preset, dependency, compiler-option, and build-layout conventions for C++ projects.
kind: contract
domain: cpp
---

# Build conventions — C++ (Tommy)

Use CMake as the project model and presets as the human-facing build interface.
These rules are platform-neutral; `gpp` owns GCC/G++ details, `msvc` owns MSVC and
clang-cl details, and `win32` owns user-mode Windows API guidance.

## Model the build with targets

- New projects target C++23 with extensions disabled.
- Put reusable logic in library targets and keep executable targets thin.
- Consumers link targets; they never compile another component's source files
  directly or reproduce its include paths and flags.
- Expose public headers through `target_include_directories` and use namespaced
  aliases such as `project::core` when a target is consumed elsewhere.
- Apply warnings, sanitizers, definitions, and options through target-scoped
  commands. Avoid directory-wide flags and global include paths.
- List source files explicitly. A build-system change should make a new source
  file visible in review rather than letting a glob change the target silently.

## Project layout

New C++/CMake projects use this structure, and **it is maintained as the
project grows** — this is not just what a scaffolder generates once at
creation, it is how the repository stays organized afterward. It is the same
regardless of toolchain: a portable CMake project builds identically under
GCC/g++ and MSVC/clang-cl, so it has no reason to keep two different trees.

- `libs/<name>/include/<name>/` — public headers for library target `<name>`.
- `libs/<name>/src/` — that library's implementation.
- `app/src/` — the thin executable target; links libraries, holds no reusable
  logic of its own.
- `tests/<name>/` — Catch2 cases for library `<name>`, mirroring `libs/<name>`'s
  shape 1:1.
- Root `CMakeLists.txt` + `CMakePresets.json` — the single build entry point;
  every `libs/*`, `app`, and `tests` directory is `add_subdirectory`'d from
  there, never built standalone.

Adding new code:

- New reusable logic starts inside the library that will consume it. Extract a
  second library target under `libs/<new-name>/` only once a second real
  consumer needs it — the same reactive-extraction rule `cpp:cpp-style` applies
  to constants. Don't pre-create empty library directories "for later."
- A new library gets a matching `tests/<new-name>/` directory the same shape as
  `libs/<new-name>/`, registered as its own target in `tests/CMakeLists.txt`.
- `app/` stays thin: it wires libraries together and owns CLI/entry-point
  concerns, it does not accumulate business logic that belongs in a library.

`gpp:gpp-scaffold` and `msvc:msvc-scaffold` both bootstrap a new project into
this exact shape; only their compiler-specific target options differ.

## Presets are the interface

Keep configure, build, and test presets in `CMakePresets.json`. A fresh clone
should be operable through named presets without remembering generator flags or
private build-directory conventions:

```text
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

Build out of source under `build/<preset>/` and export
`compile_commands.json` where the selected generator supports it. Do not commit
build output.

## Dependencies

Follow `cpp:cpp-libraries` before adding one. When CMake owns a source
dependency, use a pinned release/tag through `FetchContent`, mark third-party
headers `SYSTEM`, and disable that dependency's unnecessary tests or packaging
targets. Do not track a floating default branch.

## Preserve the repository's established shape

These are defaults for new work, not permission to reorganize an existing
project incidentally. Follow the repository's current target layout unless the
task actually requires an architectural change.
