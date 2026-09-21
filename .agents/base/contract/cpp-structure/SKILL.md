---
name: cpp-structure
description: Generic C++ project folder/file layout — where library, app, and test code lives, and how to extend it as a project grows.
kind: contract
domain: cpp
---

# Project structure — C++ (Tommy)

For a repository containing one product, new C++/CMake projects use this
structure as the normal single-product rule of thumb, and **it is maintained as
the project grows** — this is not just what a scaffolder generates once at
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
  there, never built standalone. See `cpp:cpp-build` for how those targets and
  presets are actually modeled.

## Preserve meaningful product boundaries

The single-product layout is a rule of thumb, not a reason to flatten a
multi-product repository. When roots such as `client/`, `driver/`, and
`shared/` represent meaningful product or ownership boundaries, keep them.
Apply the app/library/test structure within each owning product instead:

```text
client/
  app/
  libs/
  tests/
driver/
  libs/
  tests/
shared/
  libs/
  tests/
```

Include only the directories that product actually needs. Product-specific
code stays under its product root; code moves to `shared/` only when multiple
products genuinely consume it. Each product-level `CMakeLists.txt` owns its
local targets, while a repository-level build may coordinate those products.

## Adding new code

- New reusable logic starts inside the owning product and library that will
  consume it. Extract a second library target under that product's
  `libs/<new-name>/` only once a second real consumer needs it — the same
  reactive-extraction rule `cpp:cpp-style` applies to constants. Don't
  pre-create empty library directories "for later."
- A new library gets a matching `tests/<new-name>/` directory within the same
  product, mirroring `libs/<new-name>/` and registered as its own target in
  that product's `tests/CMakeLists.txt`.
- `app/` stays thin: it wires libraries together and owns CLI/entry-point
  concerns, it does not accumulate business logic that belongs in a library.

## Preserve the repository's established shape

This is the default for new work, not permission to reorganize an existing
project incidentally. Follow a repository's current directory layout unless
the task actually requires an architectural change.

`gpp:gpp-scaffold` and `msvc:msvc-scaffold` both bootstrap a new single-product
project into this default shape; only their compiler-specific target options
differ.
