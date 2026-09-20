---
name: gcc-toolchain
description: GCC, g++, GDB, and Linux-specific C++ toolchain conventions layered on cpp.
kind: contract
domain: cpp
---

# g++ / Linux conventions — C++ (Tommy)

How I write portable / Linux-native C++. These rules sit **on top of** the
`base` plugin, whose naming, initialization, learning, and std-first
dependency rules still hold. This file adds only the GCC / GNU / Linux toolchain
layer. API selection, including `win32`, remains independent.

## The toolchain — GCC / g++

**Linux-oriented work uses GCC (`g++`).** New projects target C++23 (g++ 16).
This is the G++/GCC tier's toolchain. It is independent of the selected OS API; the G++ and MSVC toolchains
are independent, neither is "the default".

- **g++** — the GNU C++ compiler (the "G" is for GNU, as in the GNU Compiler
  Collection, GCC).
- **gdb** — the debugger here.
- **perf** — the profiler to learn for Linux work; not started yet.
- **GNU / Linux conventions** — I came from Windows, so explain Linux/toolchain
  conventions (the OS/hardware boundary, shells, paths, linking) when relevant.

## Project layout

New G++/CMake projects use this structure, and **it is maintained as the project
grows** — this is not just what `gpp:gpp-scaffold` bootstraps once, it is how the
repository stays organized afterward:

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
  consumer needs it — the same reactive-extraction rule `base:cpp-style` applies
  to constants. Don't pre-create empty library directories "for later."
- A new library gets a matching `tests/<new-name>/` directory the same shape as
  `libs/<new-name>/`, registered as its own target in `tests/CMakeLists.txt`.
- `app/` stays thin: it wires libraries together and owns CLI/entry-point
  concerns, it does not accumulate business logic that belongs in a library.

This is a G++/CMake-community convention (cmake-init, cpp-best-practices style),
**not** a platform-neutral rule — `msvc:msvc-scaffold` deliberately starts flat
(`src/main.cpp`, no library split, no tests) following Visual-Studio-console-app
convention instead; see that skill before assuming this shape applies there too.
Per `base:cpp-build`, these are defaults for new work, not permission to
reorganize an existing repository that has already established a different
shape.

## Learning calibration

- GCC/g++ is comfortable for compiling ordinary C++, and GDB basics such as
  breakpoints have been used.
- GNU's project/toolchain history, Linux linking and loader behavior, shell and
  path conventions, and `perf` still need explanation before they are assumed.

## See also

- `base` — the platform-neutral compatibility base, which still applies here.
- The legacy `windows` package is the combined MSVC/Win32 compatibility layer; migrate to the explicit split before selecting a different compiler/API combination.
- `base:cpp-direction` — the platform-neutral skill tree this toolchain choice fills.
- `gpp:gpp-scaffold` — bootstraps a new project into the layout described above.
