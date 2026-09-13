# g++ / Linux conventions — C++ (Tommy)

How I write portable / Linux-native C++. These rules sit **on top of** the
`base` plugin, whose naming, initialization, learning, and std-first
dependency rules still hold. This file adds only the GCC / GNU / Linux toolchain
layer; `windows` is the independent MSVC / Win32 sibling.

## The toolchain — GCC / g++

**Portable and Linux work uses GCC (`g++`).** New projects target C++23 (g++ 16).
This is the GCC/Linux tier's toolchain — the sibling to the Windows tier's MSVC; the two
are independent, neither is "the default".

- **g++** — the GNU C++ compiler (the "G" is for GNU, as in the GNU Compiler
  Collection, GCC).
- **gdb** — the debugger here.
- **GNU / Linux conventions** — I came from Windows, so explain Linux/toolchain
  conventions (the OS/hardware boundary, shells, paths, linking) when relevant.
- **MinGW** (GCC that emits native Windows `.exe`s) is *not* used for native
  Windows work — that's the `windows` plugin's MSVC job. It only matters if I
  ever want a GCC-built Windows binary, which I don't by default.

## See also

- `base` — the platform-agnostic base, which still applies here.
- `windows` — the sibling MSVC / Win32 tier.
- `base:cpp-direction` — the skill tree containing the GCC / g++ / GDB picks.
