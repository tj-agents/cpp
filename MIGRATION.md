# Migration to the layered C++ marketplace

The canonical public packages are `base@cpp-agents`, `windows@cpp-agents`, and `gcc@cpp-agents`. They replace the older repository/package split without silently invalidating installed repositories.

## Compatibility window

The compatibility window ends after **2027-03-31**.

| Retired identity | Classification | Replacement | Window |
|---|---|---|---|
| `cpp-standards@cpp-agents` | Compatibility alias generated from the `base` source | `base@cpp-agents` | Remove after 2027-03-31 |
| `gpp-standards@cpp-agents` | Compatibility alias generated from the `gcc` source; retains the legacy `gpp-toolchain` skill | `gcc@cpp-agents` and `gcc:gcc-toolchain` | Remove after 2027-03-31 |
| `windows-standards@windows-agents` | Frozen migration snapshot in the archived `windows-agents` repository | `windows@cpp-agents` | Remove after 2027-03-31 |
| `agent-process:*` | Erroneous retired workflow identity | `concertable:*` from `concertable@agent-standards` | No compatibility use in generated routes |

References in this file, compatibility manifests/metadata/tests, and the archived windows-agents migration notice are intentional. Occurrences in canonical standards, hooks, route output, examples, or new consumer configuration are errors. Historical project documents may retain an old name only when changing it would falsify a dated record; each such survivor must be reported explicitly.

## Safe migration order

1. Refresh `cpp-agents` after the layered release merges.
2. Install `base@cpp-agents` and required platform layers before changing routes.
3. Regenerate `.agents/skill-routes.json` with `generic`, `windows`, or `gcc`; use repeated `--layer`
   arguments only for a repository that genuinely spans more than one platform layer.
4. Confirm Codex and Claude resolve the new packages and route identifiers.
5. Remove old packages. A short overlap can emit duplicate base session context because both base packages remain standalone during migration; it does not duplicate authored rules or write-time routes.
6. Remove the `windows-agents` marketplace only after no enabled plugin or repository configuration uses it.

That sequence is complete for every known consumer. `windows-agents` was archived on 2026-09-15 and is
retained read-only only for unknown legacy installations during the compatibility window.

Codex native-Windows example:

```powershell
codex plugin marketplace upgrade cpp-agents
codex plugin add base@cpp-agents
codex plugin add windows@cpp-agents
python <cpp-agents>/.agents/gen_skill_routes.py --kind windows --into <project>
codex plugin remove cpp-standards@cpp-agents
codex plugin remove windows-standards@windows-agents
```

Claude Code native-Windows example:

```text
/plugin marketplace update cpp-agents
/plugin install base@cpp-agents
/plugin install windows@cpp-agents
/plugin uninstall cpp-standards@cpp-agents
/plugin uninstall windows-standards@windows-agents
```

For GCC/Linux, install `base + gcc`, generate with `--kind gcc`, and remove `gpp-standards@cpp-agents`. Generic-only repositories install `base` and generate with `--kind generic`.

A cross-toolchain repository installs all three and generates the composed table explicitly:

```powershell
python <cpp-agents>/.agents/gen_skill_routes.py --layer windows --layer gcc --into <project>
```

## Repository setup

Each consumer keeps project facts in `AGENTS.md` and a one-line `CLAUDE.md` containing `@AGENTS.md`. The generated route table supplies technical and workflow standards; project instruction files must not restate them.
