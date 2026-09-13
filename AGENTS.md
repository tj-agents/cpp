# cpp-agents — working rules

This repository authors Tommy's shared C++ technical standards and delivers them to Claude Code and Codex as one layered marketplace. Read [ARCHITECTURE.md](ARCHITECTURE.md) before changing structure and [MIGRATION.md](MIGRATION.md) before changing a public identity or compatibility promise.

## Keep the three ownership layers exact

- Generic modern C++, CMake, testing, dependency, style, learning, direction, or knowledge rules belong under `standards/cpp/` and ship in `base`.
- Native Windows, Win32, Unicode, MSVC/clang-cl, WIL, native-resource, Windows CMake, or Windows-learning rules belong under `standards/windows/` and ship in `windows`.
- GCC, g++, GDB, or Linux-specific rules belong under `standards/gcc/` and ship in `gcc`.
- Workflow and repository-process rules remain in `Concertable/agent-standards`; generated routes use its published `concertable:*` identifiers.

Never author a rule in a generated plugin tree. Temporary compatibility packages are generated delivery copies with a declared removal date, not additional sources.

## Keep both harnesses valid

Shared standards, routers, and hook logic are authored under `standards/` and `.agents/`. `pwsh .agents/sync-generated.ps1` produces Claude and installable-plugin forms. A change that leaves either harness stale is incomplete.

Before committing, run:

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python .agents/gen_skill_routes.py --self-test
python -m unittest discover -s .agents/hooks/tests
python -m unittest discover -s .agents/tests
```

Before changing the external `concertable:*` contract, fetch its origin and run the suite with `AGENT_STANDARDS_SOURCE` pointing at an exact checkout of the pinned `Concertable/agent-standards` commit. That release gate requires authenticated `gh` access and binds the commit to the declared private repository. CI independently verifies the checked-in Git tree proof and GitHub signature. Git, Python, PowerShell 7, and GnuPG are validation prerequisites; Git for Windows supplies the supported GPG fallback.

Also validate every `plugins/*` directory with the available Codex and Claude validators. Preserve marketplace ordering: canonical `base`, `windows`, `gcc` first; compatibility aliases last.
