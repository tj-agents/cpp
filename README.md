# cpp

C++ guidance is authored once under `.agents/` and published as four independent plugins.
The canonical repository is [`tj-agents/cpp`](https://github.com/tj-agents/cpp); select its plugins from the [shared `tj-agents` marketplace](https://github.com/tj-agents/marketplace#readme).

| Plugin | Owns | Requires |
|---|---|---|
| `cpp@tj-agents` | Platform-neutral C++, CMake, testing, dependencies, learning, and knowledge | — |
| `gpp@tj-agents` | G++, GCC, GDB, and Linux toolchain details | `cpp` |
| `msvc@tj-agents` | MSVC/clang-cl toolchain details and the reusable console scaffold | `cpp` |
| `win32@tj-agents` | User-mode Win32, Unicode, WIL, callbacks, and native resources | `cpp` |

Compiler and API choices are separate. A console library can select `cpp + msvc` without
Win32 guidance. A Win32 project can select `cpp + win32 + gpp` or `cpp + win32 + msvc`.
The host operating system never silently chooses a compiler.

Use plugin-qualified capability names: `cpp:style`, `cpp:build`, `cpp:domain-design`, `cpp:mixins`,
`gpp:toolchain`, `msvc:scaffold`, and `win32:style`. The plugin supplies the scope, so the
capability does not repeat it. `cpp:domain-design` covers records, invariants, values,
operations, typed errors, and external state without requiring a domain layer. `cpp:mixins`
separately owns CRTP, behavior-provider, and policy-style composition; mixins are not a
domain-driven-design concern.

Canonical definitions live at:

- `.agents/base/<kind>/<name>/SKILL.md`
- `.agents/gpp/<kind>/<name>/SKILL.md`
- `.agents/msvc/<kind>/<name>/SKILL.md`
- `.agents/win32/<kind>/<name>/SKILL.md`

`.agents/plugins/sources.json` maps those sources into generated `.codex/skills/`,
`.claude/skills/`, and self-contained `plugins/*` packages. `.agents/skills/` does not exist;
`.agents/` remains the sole canonical shared tree.

Each canonical package ships `harness.json` from
`.agents/plugins/manifests/harness/<plugin>.json`. These declarations name the
`tj-agents` marketplace, existing package prerequisites, source inputs, and the
cpp SessionStart hook for both hosts. They request no permanent permissions.

Scaffolds compose the same way as the plugins:

| Utility | Produces |
|---|---|
| `gpp:scaffold` | `cpp + gpp` library + console project with G++ presets (`dev` with sanitizers, `release`, `gdb`) |
| `msvc:scaffold` | `cpp + msvc` library + console project with MSVC presets (`dev`, `release`, `asan`) and PowerShell helpers |
| `win32:scaffold` | converts either result's `app` target into a Win32 GUI application (`cpp + toolchain + win32`) |

The platform-neutral templates they share (formatter, analysis and editor configuration and the
`libs/core`, `app` and `tests` sources) are owned by `.agents/base/utility/scripts/templates/` and
copied into every package that uses them.

Generate and verify outputs with:

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
```

See MIGRATION.md for canonical selection and flat host-adapter details.
