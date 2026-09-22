---
name: scaffold
description: Create a small MSVC C++ project with a library target and Catch2 tests from reusable CMake presets and PowerShell helpers, or reuse those helpers in a compatible existing project.
kind: utility
domain: cpp
---

# MSVC project scaffold

Use `msvc:toolchain` for toolchain decisions. This skill supplies an initial
**library + console application** with CMake/Ninja presets, Catch2 tests, and small
PowerShell entry points, in the project layout `cpp:structure` defines — the same
shape `gpp:scaffold` produces for G++. Only the compiler-specific target options
(warnings flags, runtime linkage) differ between the two; the directory structure
does not. It is editor-independent and has no Win32, WIL, WinWrap or third-party
dependency beyond Catch2 by default. It does not scaffold a driver, GUI framework or
DLL ABI by relabeling a console target. Choose the appropriate project model when
one of those output types is requested.

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

Pass `-FormatConfig <existing-.clang-format>` and `-TidyConfig <existing-.clang-tidy>` to
copy the user's actual configurations byte for byte. Locate them before generating when
available. Otherwise report the omission; do not fabricate the user's formatter policy.
The generator does not search the machine or download tools and dependencies.

## Build and adapt

```powershell
./scripts/Build.ps1 -Test
./build/dev/bin/my_tool.exe
./scripts/Build.ps1 -Configuration Release
```

`Enter-DevShell.ps1` uses component-filtered `vswhere` and Microsoft's Developer PowerShell
launcher. An explicit `-VsInstallPath` selects an installed instance. Build calls CMake
presets and checks native exit codes. `-Fresh` resets CMake configuration after a toolchain
change; a different architecture/generator should use its own build directory and presets.

The sample `core::greeting()` function and its Catch2 case exist only to prove the scaffold
builds and tests end to end — replace them with real logic. `Build.ps1 -Test` runs the
selected CTest preset. Keep reusable logic in `libs/core`; extract a second library target
under `libs/<new-name>/` only once a second real consumer needs it, per `cpp:structure`.

For an existing repository, inspect its build entry points and preserve them. Reuse an
individual helper only where it fits; do not run the new-project generator over the tree.
The older workspace `newcpp` script retains its existing generic/GUI behavior. This MSVC
starter's authored home is cpp-agents; changes do not silently migrate older projects.

## Validation and publication

Generate into a fresh scratch directory, parse the generated PowerShell and JSON, build
and run with real MSVC, and exercise rejection of existing destinations. Check C++20 and
C++23 separately if both are offered. Report missing tools as prerequisites.

The skill, script and templates are authored once under `.agents/msvc/utility/` and copied to
plugin payloads by `sync-generated.ps1`; never edit the generated copies. Future WinWrap guidance belongs in
the Win32 scope once a tested library API and consumption contract are ready. It must
describe its supported native operations rather than make every MSVC project depend on it.
