---
name: msvc-toolchain
description: Generic MSVC and clang-cl environment, SDK selection, build configuration, ABI, runtime linkage, and editor diagnostics for C++ applications and libraries.
kind: contract
domain: cpp
---

# MSVC toolchain conventions

Use this standard for MSVC or clang-cl builds of C++ programs and libraries, including
projects that never call Win32 directly. It owns compiler/toolchain decisions;
`windows:win32-style` owns application-facing Windows APIs and resource ownership.
Generic C++ language, dependency and CMake conventions remain in the base layer.

## Discover the actual toolchain

- Separate the editor, Visual Studio installation, compiler toolset, Windows SDK, build
  system, host architecture and target architecture. VS Code and Neovim do not require
  using the Visual Studio IDE, but they do need the project's real build environment.
- Inspect existing project/preset requirements before selecting or upgrading a compiler.
  An installed Visual Studio edition does not prove the C++ components exist; use
  `vswhere` component filtering and verify the selected compiler and SDK files.
- Record reproducible versions in the consuming repository. Check current Microsoft
  support documentation for new toolchains; this standard does not pin one Visual Studio
  release, SDK version or architecture for every project.
- For direct compiler/Ninja builds, initialize the installed Developer Command Prompt or
  Developer PowerShell for the chosen host/target pair. Do not reconstruct INCLUDE/LIB/PATH
  from another installation. C++ MSBuild projects select toolset/SDK through project
  evaluation; inspect that selection too.

[Microsoft command-line build environment](https://learn.microsoft.com/en-us/cpp/build/building-on-the-command-line).

## Build model and configuration

- New ordinary projects follow the base CMake/preset convention. Preserve an existing
  `.vcxproj`/MSBuild build unless migration is requested. Specialized output types use
  their documented toolchain; renaming an executable does not supply its runtime contract.
- Choose Ninja with an initialized MSVC environment or a supported Visual Studio generator
  deliberately. Keep generator, architecture and compiler stable within a build directory;
  use another directory when changing them.
- Apply settings to relevant targets or scoped MSBuild property/item groups. Keep machine
  paths local, quote paths with spaces correctly, and propagate failing tool exit codes.
- Follow the base language-version default for new code, retaining a legacy project's
  selected language/runtime contract until an upgrade is requested and verified. Check
  support in the compiler; a language switch is not a promise of full conformance.
- For ordinary modern application targets, start from `/W4`, `/permissive-`, `/utf-8` and
  the chosen language mode. Set exceptions and RTTI for the runtime/library contract;
  `/EHsc` is the normal exception-enabled application choice, not universal to all outputs.
  Keep warning policy local to owned code.

[MSVC option reference](https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options),
[CMake presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html).

## ABI, runtime and dependencies

- MSVC and clang-cl target the Microsoft ABI. MinGW GCC/clang++ is a different toolchain,
  not a fallback for a missing MSVC dependency. Verify compatibility of the particular
  compiler, library and target rather than assuming it from the executable's name.
- Choose static or dynamic CRT linkage (`/MT` or `/MD`, and debug variants) for the
  deployment contract. Keep linked objects/libraries consistent, including configuration
  and iterator-debug settings. Resolve mismatches instead of suppressing them through
  blanket default-library exclusions.
- In CMake use `MSVC_RUNTIME_LIBRARY`, rather than replacing global flag strings.
  DLL boundaries also need explicit allocation/freeing ownership; matching CRT flags alone
  do not make arbitrary C++ ABI boundaries safe.
- Distinguish SDK import libraries, static libraries and DLLs. Link required system
  libraries and verify deployed dependencies. Do not require WIL, GUI libraries or Win32
  preprocessor macros in a library that does not use those interfaces; use `windows:win32-style` when
  that boundary exists.

[Microsoft CRT linkage options](https://learn.microsoft.com/en-us/cpp/build/reference/md-mt-ld-use-run-time-library),
[CMake runtime property](https://cmake.org/cmake/help/latest/prop_tgt/MSVC_RUNTIME_LIBRARY.html).

## Editors, diagnostics and evidence

### PowerShell entry points

PowerShell is a conventional Windows automation layer, not a C++ language requirement.
Microsoft provides Developer PowerShell for command-line tooling. Small `.ps1` helpers may
initialize that environment and invoke CMake/MSBuild; target definitions, dependencies and
compiler options stay in the build model. The `windows:msvc-scaffold` supplies reusable
examples. [Microsoft Developer PowerShell](https://learn.microsoft.com/en-us/visualstudio/ide/reference/command-prompt-powershell).

Use script-relative paths, typed/validated parameters, literal filesystem paths and argument
arrays. Fail on PowerShell errors and explicitly check external-tool exit codes; `$ErrorActionPreference`
alone does not reliably propagate native failures across supported PowerShell versions.
Restore location in `finally`. Keep normal builds unprivileged; installation and machine
configuration are explicit separate operations. Do not embed execution-policy bypasses,
machine-specific compiler paths, automatic tool upgrades or restarts in a build helper.

### Editor and analysis configuration

- Point editor tooling at the selected build configuration. Export a compile database when
  supported; do not invent a second flag list to quiet the editor. Launch the editor from
  the configured shell when it needs that environment.
- When a workspace has sources from more than one build model, scope clangd's compilation
  databases by source root in `.clangd`; each source root must use commands evaluated by its
  own build system. A `C_Cpp.default.compileCommands` setting configures Microsoft C/C++
  IntelliSense, not clangd. Do not disable that extension in favor of clangd until every
  edited source root has a valid clangd command.
- Reuse the actual clang-format/clang-tidy configurations. A formatter's distribution does
  not determine the program's ABI. clang-tidy needs compatible flags and headers; report
  a parsing/toolchain failure separately from a clean analysis result.
- Build with the selected compiler before treating editor diagnostics as authoritative.
  Keep matching PDBs, run appropriate tests, and distinguish compile/link, execution,
  packaging and deployment evidence.
- Report a missing compiler, SDK, library or specialized tool as a concrete prerequisite.
  Do not substitute another ABI, fake platform headers, or claim an unrun build.

## Skill-tree picks and calibration

This toolchain fills the compiler, debugger and profiler rows of `base:cpp-direction` when a
project selects MSVC:

- **Compiler** — MSVC `cl` (clang-cl where a project chooses it).
- **Debugger** — the Visual Studio debugger engine; `windows:msvc-scaffold` configures it for
  VS Code as `cppvsdbg`.
- **Profiler** — not chosen yet.

None of these is recorded as known. Explain the Developer PowerShell environment, CRT
selection, PDBs and the debugger before relying on them, and update `base:cpp-knowledge` only
after Tommy demonstrates the concept.
