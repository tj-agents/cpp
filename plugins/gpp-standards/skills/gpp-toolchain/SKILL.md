---
name: gpp-toolchain
description: GCC, g++, GDB, and Linux-specific C++ conventions layered on the platform-neutral base plugin.
kind: contract
domain: cpp
---

# g++ / Linux conventions — C++ (Tommy)

How I write portable / Linux-native C++. These rules sit **on top of** the
`base` plugin, whose naming, initialization, learning, and std-first
dependency rules still hold. This file adds only the GCC / GNU / Linux toolchain
layer; `windows` is the independent MSVC / Win32 sibling.

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

- `base` — the platform-agnostic base, which still applies here.
- `windows` — the sibling MSVC / Win32 tier.
- `cpp-standards:cpp-direction` — the platform-neutral skill tree this toolchain choice fills.
