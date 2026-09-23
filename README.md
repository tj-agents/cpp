# cpp

C++ guidance is authored once under `.agents/` and published as four independent plugins.
The canonical repository is [`tj-agents/cpp`](https://github.com/tj-agents/cpp); the marketplace ID remains `cpp-agents`.

| Plugin | Owns | Requires |
|---|---|---|
| `cpp@cpp-agents` | Platform-neutral C++, CMake, testing, dependencies, learning, and knowledge | — |
| `gpp@cpp-agents` | G++, GCC, GDB, and Linux toolchain details | `cpp` |
| `msvc@cpp-agents` | MSVC/clang-cl toolchain details and the reusable console scaffold | `cpp` |
| `win32@cpp-agents` | User-mode Win32, Unicode, WIL, callbacks, and native resources | `cpp` |

Compiler and API choices are separate. A console library can select `cpp + msvc` without
Win32 guidance. A Win32 project can select `cpp + win32 + gpp` or `cpp + win32 + msvc`.
The host operating system never silently chooses a compiler.

Use plugin-qualified capability names: `cpp:style`, `cpp:build`, `cpp:domain-design`,
`gpp:toolchain`, `msvc:scaffold`, and `win32:style`. The plugin supplies the scope, so the
capability does not repeat it. `cpp:domain-design` covers records, invariants, values,
operations, typed errors, and external state without requiring a domain layer.

Canonical definitions live at:

- `.agents/base/<kind>/<name>/SKILL.md`
- `.agents/gpp/<kind>/<name>/SKILL.md`
- `.agents/msvc/<kind>/<name>/SKILL.md`
- `.agents/win32/<kind>/<name>/SKILL.md`

`.agents/plugins/sources.json` maps those sources into generated `.codex/skills/`,
`.claude/skills/`, and self-contained `plugins/*` packages. `.agents/skills/` does not exist;
`.agents/` remains the sole canonical shared tree.

Scaffolds compose the same way as the plugins:

| Utility | Produces |
|---|---|
| `gpp:scaffold` | `cpp + gpp` library + console project with G++ presets (`dev` with sanitizers, `release`, `gdb`) |
| `msvc:scaffold` | `cpp + msvc` library + console project with MSVC presets (`dev`, `release`, `asan`) and PowerShell helpers |
| `win32:scaffold` | converts either result's `app` target into a Win32 GUI application (`cpp + toolchain + win32`) |

The platform-neutral templates they share (formatter, analysis and editor configuration and the
`libs/core`, `app` and `tests` sources) are owned by `.agents/base/utility/scripts/templates/` and
copied into every package that uses them. Each generated project carries the route profile for its
exact composition, rendered by the route generator at sync time.

Generate and verify outputs with:

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python -B .agents/gen_skill_routes.py --self-test
python -B .agents/sync_generated.py --record-package-versions   # after a version bump
```

Generate a consuming repository profile explicitly:

```powershell
python .agents/gen_skill_routes.py --toolchain msvc --into C:/source/project
python .agents/gen_skill_routes.py --toolchain gpp --api win32 --into C:/source/project
python .agents/gen_skill_routes.py --api win32 --into C:/source/project
```

Legacy `--kind gcc` and `--kind windows` inputs remain accepted for migration. New profiles
emit only `cpp`, `gpp`, `msvc`, and `win32` identities and contain no compulsory process-plugin
route. Process workflows may be installed separately from their shared engineering owner.

Compatibility packages `base`, `gcc`, `windows`, `cpp-standards`, and `gpp-standards` remain
through 2027-03-31. The old `windows` package is a generated combined MSVC plus Win32 bundle;
consumers must choose the explicit split when migrating.
Old capability identifiers also remain as generated compatibility entries through that date.
See [MIGRATION.md](MIGRATION.md) for the complete name mapping and flat host-adapter distinction.
