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

Unlike `windows:msvc-scaffold`, this generator does not accept an external
`.clang-format`/`.clang-tidy` to copy byte-for-byte — there is no separate
canonical config to preserve here, so the bundled templates *are* the
canonical defaults (they match `cpp-standards:cpp-style` exactly). Edit the generated
project's copies afterward if a specific project needs to diverge.

## Build and adapt

```bash
cd my_tool
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
```

No Developer-shell initialization step is needed — unlike MSVC, the G++/Ninja
toolchain is already on `PATH` once installed. `build/dev` carries sanitizers
(`-fsanitize=address,undefined`) and debug symbols; `build/release` is the
optimized configuration. Keep reusable logic in `libs/core` and thin executable
code in `app`; extract a second library target once a second consumer appears,
following `cpp-standards:cpp-style`'s reactive-extraction rule.

The sample `core::greeting()` function and its Catch2 case exist only to prove
the scaffold builds and tests end to end — replace them with real logic before
treating the project as more than a skeleton.

For an existing repository, inspect its build entry points and preserve them;
do not run the generator over an existing tree. The workspace `newcpp` command
wraps this script with Tommy's personal defaults (destination, `git init`,
editor launch) — those conveniences are not part of the shared repo tool.

## Validation and publication

Generate into a fresh scratch directory, parse the generated `CMakePresets.json`
and the script itself (`bash -n`), build and run with real G++, and exercise
rejection of existing destinations. Check C++20 and C++23 separately.

The skill, script and templates are authored once under `.agents/gpp/utility/`
and copied to plugin payloads by `sync-generated.ps1`; never edit the generated
copies.
