# cpp-agents

Tommy's layered C++ standards marketplace for Claude Code and Codex. One repository owns the generic C++ corpus and both supported platform/toolchain deltas.

## Public plugins

| Plugin | Responsibility | Requires |
|---|---|---|
| `base@cpp-agents` | Modern platform-neutral C++, CMake, dependency policy, testing, style, learning guidance, direction, and general C++ knowledge | — |
| `windows@cpp-agents` | Native Windows development: Win32, Unicode, MSVC and clang-cl, WIL, native-resource ownership, Windows CMake, and Windows learning guidance | `base@cpp-agents` |
| `gcc@cpp-agents` | GCC, g++, GDB, and Linux-oriented native C++ development | `base@cpp-agents` |

The layers compose. Install `base + windows` for a native Windows repository and `base + gcc` for a GCC/Linux repository. A project that genuinely spans both toolchains may install all three.

## Install

Claude Code:

```text
/plugin marketplace add tomjseery/cpp-agents
/plugin install base@cpp-agents
/plugin install windows@cpp-agents
```

Substitute `gcc@cpp-agents` for `windows@cpp-agents` on a GCC/Linux machine or project.

Codex:

```powershell
codex plugin marketplace add https://github.com/tomjseery/cpp-agents
codex plugin add base@cpp-agents
codex plugin add windows@cpp-agents
```

Substitute `gcc@cpp-agents` for the Windows layer where appropriate. Install `concertable@agent-standards` separately in both harnesses; it owns workflow, planning, review, delivery, repository management, and the write-time skill router.

## Repository routing

`base` carries the C++ session-detection hook. An explicit generated route kind wins over the host platform; otherwise native Windows markers select `windows`, a Linux host selects `gcc`, and every C++ repository receives `base`.

Generate deterministic write-time routes with:

```powershell
python .agents/gen_skill_routes.py --kind generic --into <project>
python .agents/gen_skill_routes.py --kind windows --into <project>
python .agents/gen_skill_routes.py --kind gcc --into <project>
python .agents/gen_skill_routes.py --layer windows --layer gcc --into <cross-toolchain-project>
```

The single `--kind` form remains the convenient and compatibility-safe input for ordinary repositories;
repeat `--layer` when a repository genuinely needs more than one platform layer. Generated tables carry
an ordered `layers` list with `base` first. They use `base:*`, `windows:*`, `gcc:*`, and `concertable:*`.
Every matching row fires, so a Windows test receives generic style/testing plus the Windows layer. Project
`AGENTS.md` files retain project facts; `CLAUDE.md` imports `AGENTS.md` so both harnesses receive the same
repository guidance.

## Compatibility migration

`cpp-standards@cpp-agents` and `gpp-standards@cpp-agents` remain generated compatibility aliases through 2027-03-31. `windows-standards@windows-agents` remains available from the deprecated forwarding repository for the same interval. New configurations must use only `base`, `windows`, and `gcc`.

Follow [MIGRATION.md](MIGRATION.md) for the install-before-route-update sequence and the exhaustive classification of retired names.

## Authoring and validation

Markdown under `standards/` and routers under `.agents/skills/` are source. `.agents/sync-generated.ps1` creates self-contained Codex and Claude plugin payloads; generated plugin files and `.claude/skills/` are never edited directly.

Validation requires Git, Python, PowerShell 7, and GnuPG. On Windows, the tests automatically use the GPG executable bundled with Git for Windows when `gpg` is not on `PATH`. Contract refreshes additionally require an authenticated GitHub CLI so the release gate can bind the pinned commit to the private `Concertable/agent-standards` repository.

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python .agents/gen_skill_routes.py --self-test
python -m unittest discover -s .agents/hooks/tests
python -m unittest discover -s .agents/tests
```

CI also validates every plugin manifest for both harnesses and rejects broken identifiers, missing dependencies, stale canonical names, generated drift, and incorrect layered activation.
