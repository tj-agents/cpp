# Migration

Consumers install `cpp` plus explicit toolchain/API plugins from the `tj-agents` marketplace.
The `cpp-agents` marketplace, its compatibility packages, and the generated alias skills are
retired and no longer published.

| Retired identity | Replacement | Rule |
|---|---|---|
| `cpp@cpp-agents`, `gpp@cpp-agents`, `msvc@cpp-agents`, `win32@cpp-agents` | the same plugin `@tj-agents` | Only the marketplace changes. |
| `base@cpp-agents` | `cpp@tj-agents` | This is unrelated to the core `base@tj-agents` plugin. |
| `gcc@cpp-agents` | `gpp@tj-agents` | `gcc:gcc-toolchain` becomes `gpp:toolchain`. |
| `windows@cpp-agents` | explicit `msvc@tj-agents`, `win32@tj-agents`, or both | The old bundle combined both; never guess one half. |
| `cpp-standards@cpp-agents` | `cpp@tj-agents` | |
| `gpp-standards@cpp-agents` | `gpp@tj-agents` | |
| `windows-standards@windows-agents` | explicit `win32@tj-agents` and, if required, `msvc@tj-agents` | Archived historical package; inspect actual use. |

Migration steps:

1. Inspect the project's compiler and API use separately.
2. Install `cpp`, then the selected `gpp` or `msvc` toolchain and optional `win32` API plugin.
3. Regenerate `.agents/skill-routes.json` with `--toolchain` and `--api`.
4. Uninstall any retired package and validate generated routes and real builds.

Examples:

```powershell
python <cpp-repository>/.agents/gen_skill_routes.py --toolchain msvc --into <console-project>
python <cpp-repository>/.agents/gen_skill_routes.py --toolchain gpp --api win32 --into <win32-project>
python <cpp-repository>/.agents/gen_skill_routes.py --api win32 --into <compiler-unspecified-project>
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

`cpp:domain-design` is new. The retired packages' `base:cpp-*`, `cpp-standards:cpp-*`,
`gcc:gcc-toolchain`, `gcc:gpp-scaffold`, `gpp-standards:gpp-*`, and combined `windows:*`
identifiers, and the previous canonical identifiers above, no longer resolve. Switch a
consumer's routes and guidance to the current identifiers.

Local `.codex/skills/` and `.claude/skills/` adapters have one flat naming space. Their
explicitly mapped names remain globally unique (`cpp-style`, `gpp-toolchain`,
`msvc-toolchain`, and so on); `cpp-domain-design` is the new adapter. Installed plugin
identifiers use the short capability names. Do not hand-edit either generated form.
