---
name: cpp-structure
description: Generic C++ project folder/file layout — where library, app, and test code lives, and how to extend it as a project grows.
kind: contract
domain: cpp
---

# Project structure — C++ (Tommy)

New C++/CMake projects use this structure, and **it is maintained as the
project grows** — this is not just what a scaffolder generates once at
creation, it is how the repository stays organized afterward. It is the same
regardless of toolchain: a portable CMake project builds identically under
GCC/g++ and MSVC/clang-cl, so it has no reason to keep two different trees.

## Layout

- `libs/<name>/include/<name>/` — public headers for library target `<name>`.
- `libs/<name>/src/` — that library's implementation.
- `app/src/` — the thin executable target; links libraries, holds no reusable
  logic of its own.
- `tests/<name>/` — Catch2 cases for library `<name>`, mirroring `libs/<name>`'s
  shape 1:1.
- Root `CMakeLists.txt` + `CMakePresets.json` — the single build entry point;
  every `libs/*`, `app`, and `tests` directory is `add_subdirectory`'d from
  there, never built standalone. See `cpp-standards:cpp-build` for how those targets and
  presets are actually modeled.

## Adding new code

- New reusable logic starts inside the library that will consume it. Extract a
  second library target under `libs/<new-name>/` only once a second real
  consumer needs it — the same reactive-extraction rule `cpp-standards:cpp-style` applies
  to constants. Don't pre-create empty library directories "for later."
- A new library gets a matching `tests/<new-name>/` directory the same shape as
  `libs/<new-name>/`, registered as its own target in `tests/CMakeLists.txt`.
- `app/` stays thin: it wires libraries together and owns CLI/entry-point
  concerns, it does not accumulate business logic that belongs in a library.

## Preserve the repository's established shape

This is the default for new work, not permission to reorganize an existing
project incidentally. Follow a repository's current directory layout unless
the task actually requires an architectural change.

`gpp:gpp-scaffold` and `msvc:msvc-scaffold` both bootstrap a new project into
this exact shape; only their compiler-specific target options differ.
