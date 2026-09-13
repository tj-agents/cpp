# Build conventions — C++ (Tommy)

Use CMake as the project model and presets as the human-facing build interface.
These rules are platform-neutral; `gcc` owns GCC/Linux details and `windows`
owns MSVC, clang-cl, and Win32 details.

## Model the build with targets

- New projects target C++23 with extensions disabled.
- Put reusable logic in library targets and keep executable targets thin.
- Consumers link targets; they never compile another component's source files
  directly or reproduce its include paths and flags.
- Expose public headers through `target_include_directories` and use namespaced
  aliases such as `project::core` when a target is consumed elsewhere.
- Apply warnings, sanitizers, definitions, and options through target-scoped
  commands. Avoid directory-wide flags and global include paths.
- List source files explicitly. A build-system change should make a new source
  file visible in review rather than letting a glob change the target silently.

## Presets are the interface

Keep configure, build, and test presets in `CMakePresets.json`. A fresh clone
should be operable through named presets without remembering generator flags or
private build-directory conventions:

```text
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

Build out of source under `build/<preset>/` and export
`compile_commands.json` where the selected generator supports it. Do not commit
build output.

## Dependencies

Follow `base:cpp-libraries` before adding one. When CMake owns a source
dependency, use a pinned release/tag through `FetchContent`, mark third-party
headers `SYSTEM`, and disable that dependency's unnecessary tests or packaging
targets. Do not track a floating default branch.

## Preserve the repository's established shape

These are defaults for new work, not permission to reorganize an existing
project incidentally. Follow the repository's current target layout unless the
task actually requires an architectural change.
