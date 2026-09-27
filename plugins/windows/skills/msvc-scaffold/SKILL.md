---
name: msvc-scaffold
description: Create a small MSVC C++ project with a library target and Catch2 tests from reusable CMake presets and PowerShell helpers, or reuse those helpers in a compatible existing project.
kind: utility
domain: cpp
---

# MSVC project scaffold

Use `windows:msvc-toolchain` for toolchain decisions. This skill supplies an initial
**library + console application** with CMake/Ninja presets, Catch2 tests, and small
PowerShell entry points, in the project layout `base:cpp-structure` defines — the same
shape `gcc:gpp-scaffold` produces for G++. Only the compiler-specific target options
(warnings flags, runtime linkage) differ between the two; the directory structure
does not. It has no Win32, WIL, WinWrap or third-party dependency beyond Catch2 by
default. Convert its `app` target into a user-mode Win32 GUI application with
`windows:win32-scaffold`; it does not scaffold a driver, GUI framework or DLL ABI by relabeling a
console target. Choose the appropriate project model when one of those output types is
requested.

## Create a project

Run the bundled [New-MsvcProject.ps1](../../resources/msvc/utility/scripts/New-MsvcProject.ps1) from PowerShell 7.
Resolve its path relative to this document, including when using an installed plugin:

```powershell
& <skill-directory>/../../resources/msvc/utility/scripts/New-MsvcProject.ps1 -Name my_tool -Destination C:/source
```

The result is `C:/source/my_tool`. Destination must already exist; the new project must
not exist. `-WhatIf` previews the destination. There is no overwrite mode or implicit
installer, Git commit, global environment change, signing or deployment step.

C++23 is the default. Pass `-CppStandard 20` for a consumer that actually requires C++20.
The initial source works in either mode; later APIs must respect the selected baseline.
Toolchain conformance must still be verified by compiling the project.

The project receives the canonical `cpp` formatter, analysis and editor configuration
(`.clang-format`, `.clang-tidy`, `.editorconfig`, `.vscode/settings.json` for clangd and
`.vscode/extensions.json` recommending the clangd and C/C++ extensions), the
shared `libs/core` + `app` + `tests` sources, and MSVC-specific files: presets, PowerShell
helpers, a `.clangd` that strips sanitizer flags clang rejects with the debug CRT, a
Visual Studio debugger (`cppvsdbg`) `.vscode/launch.json`, `AGENTS.md`/`CLAUDE.md` project
facts and the `cpp` + `msvc` route profile in `.agents/skill-routes.json`. Pass
`-FormatConfig <existing-.clang-format>` and `-TidyConfig <existing-.clang-tidy>` to copy a
project's own configurations byte for byte instead. The generator does not search the
machine or download tools and dependencies.

The scaffold's `.clangd` maps only its CMake-owned `app`, `libs`, and `tests` directories
to `build/dev/compile_commands.json`. If the repository adds a source root built by another
system, generate that system's compile database and add a separate path-scoped `.clangd`
entry. Do not use a workspace-wide CMake database or a C/C++ extension setting as clangd's
configuration for those sources.

## Build and adapt

```powershell
./scripts/Build.ps1 -Test
./build/dev/bin/my_tool.exe
./scripts/Build.ps1 -Configuration Release
./scripts/Build.ps1 -Configuration Asan -Test
```

`Enter-DevShell.ps1` uses component-filtered `vswhere` and Microsoft's Developer PowerShell
launcher. An explicit `-VsInstallPath` selects an installed instance. `Open-Editor.ps1`
enters that shell, then opens the project in `code` (or `-Editor <command>`) so clangd
inherits the MSVC and Windows SDK environment; clangd's own Visual Studio discovery is
unreliable (see `windows:msvc-toolchain`). A window that is already open keeps its original
environment. Build calls CMake
presets and checks native exit codes. `-Fresh` resets CMake configuration after a toolchain
change; a different architecture/generator should use its own build directory and presets.
Warnings and AddressSanitizer are target-scoped through the `<project>_warnings` and
`<project>_sanitize` interface libraries, following `base:cpp-build`. The `asan` preset enables
the sanitizer and requires the Visual Studio "C++ AddressSanitizer" component
(`Microsoft.VisualStudio.Component.VC.ASAN`); `Build.ps1 -Configuration Asan` selects an
installation that has it. `cmake --install` places the executable in
`%LOCALAPPDATA%\Microsoft\WindowsApps` unless a prefix is given.

The sample `core::greeting()` function and its Catch2 case exist only to prove the scaffold
builds and tests end to end — replace them with real logic. `Build.ps1 -Test` runs the
selected CTest preset. Replace `libs/core` with modules that own the application's real
responsibilities. Add a library target for a cohesive API, dependency control, independent
testing, or reuse, per `base:cpp-structure`; it does not require a second consumer.

For an existing repository, inspect its build entry points and preserve them. Reuse an
individual helper only where it fits; do not run the new-project generator over the tree.
A personal wrapper may add conveniences such as a default destination or `git init`; those
stay in the consuming workspace. This MSVC starter's authored home is `tj-agents/cpp`;
changes do not silently migrate older projects.

## Validation and publication

Generate into a fresh scratch directory, parse the generated PowerShell and JSON, build
and run with real MSVC, and exercise rejection of existing destinations. Check C++20 and
C++23 separately if both are offered. Report missing tools as prerequisites.

The skill, script and MSVC templates are authored once under `.agents/msvc/utility/`; the
shared templates belong to `.agents/base/utility/scripts/` and the route profile is rendered
by the route generator. `sync-generated.ps1` copies all of them into the plugin payloads;
never edit the generated copies. Future WinWrap guidance belongs in
the Win32 scope once a tested library API and consumption contract are ready. It must
describe its supported native operations rather than make every MSVC project depend on it.
