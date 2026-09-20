---
name: gpp-toolchain
description: GCC, g++, GDB, and Linux-specific C++ toolchain conventions layered on cpp.
kind: contract
domain: cpp
---

# g++ / Linux conventions — C++ (Tommy)

How I write portable / Linux-native C++. These rules sit **on top of** the
`cpp` plugin, whose naming, initialization, learning, and std-first
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

## Learning calibration

- GCC/g++ is comfortable for compiling ordinary C++, and GDB basics such as
  breakpoints have been used.
- GNU's project/toolchain history, Linux linking and loader behavior, shell and
  path conventions, and `perf` still need explanation before they are assumed.

## See also

- `cpp` — the platform-neutral C++ base, which still applies here.
- `msvc` — the alternative MSVC/clang-cl toolchain when a project selects it.
- `win32` — an optional user-mode Windows API layer that does not choose a compiler.
- `cpp-standards:cpp-direction` — the platform-neutral skill tree this toolchain choice fills.
