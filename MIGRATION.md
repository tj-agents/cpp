# Migration

New consumers install `cpp` plus explicit toolchain/API plugins. Existing identities remain as
generated compatibility packages through 2027-03-31.

| Existing identity | Replacement | Rule |
|---|---|---|
| `base@cpp-agents` | `cpp@cpp-agents` | This is unrelated to common `base@base-agents`. |
| `gcc@cpp-agents` | `gpp@cpp-agents` | `gcc:gcc-toolchain` becomes `gpp:gpp-toolchain`. |
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
python <cpp-repository>/.agents/gen_skill_routes.py --toolchain msvc --into <console-project>
python <cpp-repository>/.agents/gen_skill_routes.py --toolchain gpp --api win32 --into <win32-project>
python <cpp-repository>/.agents/gen_skill_routes.py --api win32 --into <compiler-unspecified-project>
```

Legacy `--kind generic`, `--kind gcc`, and `--kind windows` remain accepted as migration input.
`windows` normalizes to the historical combined `msvc + win32` profile. New output always uses the
four current identities. Do not edit historical provenance or signatures to simulate compatibility.
