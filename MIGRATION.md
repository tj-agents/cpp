# Migration

New consumers install `cpp` plus explicit toolchain/API plugins. Existing identities remain as
generated compatibility packages through 2027-03-31.

| Existing identity | Replacement | Rule |
|---|---|---|
| `base@cpp-agents` | `cpp@cpp-agents` | This is unrelated to common `base@base-agents`. |
| `gcc@cpp-agents` | `gpp@cpp-agents` | `gcc:gcc-toolchain` becomes `gpp:toolchain`. |
| `windows@cpp-agents` | explicit `msvc`, `win32`, or both | The compatibility bundle retains both; never guess one half. |
| `cpp-standards@cpp-agents` | `cpp@cpp-agents` | Remove after the compatibility window. |
| `gpp-standards@cpp-agents` | `gpp@cpp-agents` | Remove after the compatibility window. |
| `windows-standards@windows-agents` | explicit `win32` and, if required, `msvc` | Archived historical package; inspect actual use. |

Migration steps:

1. Inspect the project's compiler and API use separately.
2. Install `cpp`, then the selected `gpp` or `msvc` toolchain and optional `win32` API plugin.
3. Regenerate `.agents/skill-routes.json` with `--toolchain` and `--api`.
4. Validate generated routes and real builds before removing compatibility packages.

Examples:

```powershell
python <cpp-agents>/.agents/gen_skill_routes.py --toolchain msvc --into <console-project>
python <cpp-agents>/.agents/gen_skill_routes.py --toolchain gpp --api win32 --into <win32-project>
python <cpp-agents>/.agents/gen_skill_routes.py --api win32 --into <compiler-unspecified-project>
```

Legacy `--kind generic`, `--kind gcc`, and `--kind windows` remain accepted as migration input.
`windows` normalizes to the historical combined `msvc + win32` profile. New output always uses the
four current identities. Do not edit historical provenance or signatures to simulate compatibility.

## Capability names

The plugin is the namespace. Use these canonical identifiers in new guidance and routes:

| Previous canonical identifier | Current identifier |
|---|---|
| `cpp:cpp-build` | `cpp:build` |
| `cpp:cpp-direction` | `cpp:direction` |
| `cpp:cpp-knowledge` | `cpp:knowledge` |
| `cpp:cpp-learning` | `cpp:learning` |
| `cpp:cpp-libraries` | `cpp:libraries` |
| `cpp:cpp-structure` | `cpp:structure` |
| `cpp:cpp-style` | `cpp:style` |
| `cpp:cpp-testing` | `cpp:testing` |
| `gpp:gpp-toolchain` | `gpp:toolchain` |
| `gpp:gpp-scaffold` | `gpp:scaffold` |
| `msvc:msvc-toolchain` | `msvc:toolchain` |
| `msvc:msvc-scaffold` | `msvc:scaffold` |
| `win32:win32-style` | `win32:style` |
| `win32:windows-cpp-knowledge` | `win32:knowledge` |
| `win32:windows-overview` | `win32:overview` |

`cpp:domain-design` is new. Legacy `base:cpp-*`, `cpp-standards:cpp-*`,
`gcc:gcc-toolchain`, `gcc:gpp-scaffold`, `gpp-standards:gpp-*`, and combined
`windows:*` identifiers retain their published spellings through 2027-03-31.
The previous canonical identifiers above resolve through generated redirects for that same
window. Upgrade the installed package before switching a consumer's routes.

Local `.codex/skills/` and `.claude/skills/` adapters have one flat naming space. Their
explicitly mapped names remain globally unique (`cpp-style`, `gpp-toolchain`,
`msvc-toolchain`, and so on); `cpp-domain-design` is the new adapter. Installed plugin
identifiers use the short capability names. Do not hand-edit either generated form.
