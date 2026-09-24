---
name: structure
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
  there, never built standalone. See `cpp:build` for how those targets and
  presets are actually modeled.

## Public header paths and dependencies

Keep an owner prefix below a public include root even when it is the root's only child:
`include/<library>/...` gives consumers distinctive paths such as `<device/protocol/identity.hpp>`.
Compilers search several include roots; storing a dependency elsewhere does not isolate
its header names. Private headers beside implementation files do not need this prefix.

Use an additional folder such as `protocol/` when it names a real contract or subsystem.
Wire records and interface/operation identifiers can form that boundary. DDD does not
prescribe the folder, and a directory does not automatically require a C++ namespace.
Name source/header files for the concept they own, such as `identity.hpp` and
`identity.cpp`; keep a type's declarations and out-of-line member definitions together
conceptually rather than creating a generic validation/errors module.

Third-party libraries keep their own source/include trees in a package cache, an out-of-source
FetchContent build directory, or `third_party/` when deliberately vendored. Do not copy them
under the product's public include root. Link dependency targets so they provide their own
include paths and transitive requirements; never put cache or build paths in `#include`.

## Organize by ownership, not composition technique

Group headers and sources by the domain concept, public resource, or stable native
protocol they implement. For example:

```text
include/acme/editor/file_drop.hpp
include/acme/protocol/command.hpp
src/editor/file_drop.cpp
```

A language mechanism such as a mixin, template, callback, or inheritance hierarchy is not
a mandatory folder category. Do not create `mixins/`, placeholder types, or public APIs
merely to make a directory look complete. Several behavior providers may belong beside
the resource or protocol they extend; introduce a common folder only when it names a real,
stable ownership boundary.

A public template may physically include support headers because its definition must be
available to consumers. Put implementation-only support under an owner-prefixed path such
as `<acme/detail/file_drop_dispatch.hpp>` when that distinction is useful. `detail/` means
the declaration has no supported compatibility contract; it is not access control, and
consumers can still include or name it at their own risk. The public header remains
responsible for presenting the complete supported API and for containing any implementation
macros it uses.

Do not create a public forwarding header for every detail file. Promote a declaration out
of `detail/` only when consumers need a supported contract. Conversely, a detail header's
physical inclusion by a public template does not make its names public API.

Keep paths independent from C++ namespaces. A folder may help humans navigate a resource
family without adding a namespace; add a namespace only when it names a real library,
subsystem, or protocol ownership boundary. Do not mirror `detail/` into namespace spelling
as a substitute for documenting its unsupported status.

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

## Model boundaries

Organize by the owning feature and actual responsibilities. A `domain` folder or library
is warranted only when a distinct model needs that boundary; passive protocol records
do not require one. Use `cpp:domain-design` to choose representations and operations
without imposing an extra architectural layer. Keep namespace hierarchy independent of
folder depth: a feature can own files and a build target without another C++ namespace.
Use public headers and target dependencies to express and enforce the module boundary.

## Adding new code

- Put new logic in the product and module that own its responsibility. Introduce a
  library target under that product's `libs/<name>/` when it establishes a cohesive API,
  controls dependencies, supports independent testing, or serves multiple consumers.
  One consumer is sufficient when the architectural boundary is useful. Keep known
  growth requirements in the design; do not pre-create empty library directories.
- A new library gets a matching `tests/<new-name>/` directory within the same
  product, mirroring `libs/<new-name>/` and registered as its own target in
  that product's `tests/CMakeLists.txt`.
- `app/` stays thin: it wires libraries together and owns CLI/entry-point
  concerns, it does not accumulate business logic that belongs in a library.

## Preserve the repository's established shape

This is the default for new work, not permission to reorganize an existing
project incidentally. Follow a repository's current directory layout unless
the task actually requires an architectural change.

`gpp:scaffold` and `msvc:scaffold` both bootstrap a new single-product
project into this default shape; only their compiler-specific target options
differ. `win32:scaffold` converts either result's `app` target into a Win32 GUI
application without changing the layout.
