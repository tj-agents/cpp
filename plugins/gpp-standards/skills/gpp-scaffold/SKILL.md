---
name: gpp-scaffold
description: Create a small G++/CMake C++ console project with a library target and Catch2 tests wired in, or reuse those templates in a compatible existing project.
kind: utility
domain: cpp
---

# G++ project scaffold

Use `gpp-standards:gpp-toolchain` for toolchain decisions. This skill supplies an initial
**library + console application** with CMake/Ninja presets and Catch2 tests, in
the project layout `cpp-standards:cpp-structure` defines — the same shape `windows:msvc-scaffold`
produces for MSVC. Only the compiler-specific target options (warnings flags,
runtime linkage) differ between the two; the directory structure does not.

## Create a project

Run the bundled [new-gpp-project.sh](../../resources/gpp/utility/scripts/new-gpp-project.sh). Resolve its
path relative to this document, including when using an installed plugin:

```bash
<skill-directory>/../../resources/gpp/utility/scripts/new-gpp-project.sh --name my_tool --destination ~/projects/cpp
```

The result is `~/projects/cpp/my_tool`. Destination must already exist; the new
project must not exist. `--dry-run` previews the destination. There is no
overwrite mode, and the script does not run `git init`, launch an editor, or
otherwise touch anything outside the new project directory.

C++23 is the default. Pass `--cpp-standard 20` for a consumer that actually
requires C++20. The initial source works in either mode; later APIs must
respect the selected baseline. Toolchain conformance must still be verified by
compiling the project.

Pass `--simple` for a single-file `CMakeLists.txt` + `main.cpp` project instead
(quick/throwaway or LeetCode-style work) — no library, no tests, no presets
beyond a single implicit build directory.

The project receives the canonical `cpp` formatter, analysis and editor configuration
(`.clang-format`, `.clang-tidy`, `.editorconfig`, `.vscode/settings.json` for clangd and
`.vscode/extensions.json` recommending the clangd and C/C++ extensions), the
shared `libs/core` + `app` + `tests` sources, and G++-specific files: presets, a `.clangd`
that reads the `dev` compile database, a GDB `.vscode/launch.json`, `AGENTS.md`/
`CLAUDE.md` project facts and the `cpp` + `gpp` route profile in `.agents/skill-routes.json`.
Edit the generated copies afterward if a specific project needs to diverge. Add the
user-mode Win32 application layer separately with `windows:win32-scaffold`.

## Build and adapt

```bash
cd my_tool
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
```

No Developer-shell initialization step is needed — unlike MSVC, the G++/Ninja
toolchain is already on `PATH` once installed.

| Preset | Purpose |
|---|---|
| `dev` | Debug with AddressSanitizer and UBSan |
| `release` | Optimized |
| `gdb` | Debug without sanitizers, for clean stepping in GDB |

Warnings and sanitizers are target-scoped through the `<project>_warnings` and
`<project>_sanitize` interface libraries, following `cpp-standards:cpp-build`; `dev` turns the sanitizer
option on. MinGW does not ship the sanitizer runtimes, so use `gdb` there. `cmake --install`
places the executable in a directory already on `PATH` (`~/.local/bin`, or
`%LOCALAPPDATA%\Microsoft\WindowsApps` on Windows) unless a prefix is given. Keep reusable
logic in `libs/core` and thin executable code in `app`; add library targets as
`cpp-standards:cpp-structure` describes.

The sample `core::greeting()` function and its Catch2 case exist only to prove
the scaffold builds and tests end to end — replace them with real logic before
treating the project as more than a skeleton.

For an existing repository, inspect its build entry points and preserve them;
do not run the generator over an existing tree. A personal wrapper may add conveniences
such as a default destination or `git init`; those stay in the consuming workspace.

## Validation and publication

Generate into a fresh scratch directory, parse the generated `CMakePresets.json`
and the script itself (`bash -n`), build and run with real G++, and exercise
rejection of existing destinations. Check C++20 and C++23 separately.

The skill, script and G++ templates are authored once under `.agents/gpp/utility/`; the
shared templates belong to `.agents/base/utility/scripts/` and the route profile is rendered
by the route generator. `sync-generated.ps1` copies all of them into the plugin payloads;
never edit the generated copies.
