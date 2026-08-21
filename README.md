# cpp-agents

Tommy's reusable C++ standards for Claude Code and Codex. The repository is an
installable marketplace, so consuming projects do not depend on where this repo
or the project is cloned.

## Plugins

| Plugin | Install where | Scope |
|---|---|---|
| `cpp-standards` | Every C++ machine | Platform-neutral style, build, testing, libraries, learning workflow, direction, and current knowledge |
| `gpp-standards` | Linux machines | GCC, g++, gdb, and Linux conventions layered on `cpp-standards` |

Native Windows conventions live in
[`tomjseery/windows-agents`](https://github.com/tomjseery/windows-agents), whose
`windows-standards` plugin layers on `cpp-standards` instead of repeating it.

## Install once per machine

Claude Code on Linux:

```text
/plugin marketplace add tomjseery/cpp-agents
/plugin install cpp-standards@cpp-agents
/plugin install gpp-standards@cpp-agents
```

Codex on Linux:

```powershell
codex plugin marketplace add https://github.com/tomjseery/cpp-agents
codex plugin add cpp-standards@cpp-agents
codex plugin add gpp-standards@cpp-agents
```

On Windows, install `cpp-standards` here and `windows-standards` from
`windows-agents`; do not install `gpp-standards` unless that machine is also used
for Linux work.

The `cpp-standards` plugin carries a session hook. In a C++ repository it adds a
short routing instruction at startup, resume, clear, and compaction. On Linux it
also selects `gpp-standards`; on Windows it selects `windows-standards` only when
the repository contains native Windows markers. The hook names skills and does
not copy their rule text into context.

For deterministic write-time routing, generate the repository table consumed
by the installed `agent-process` plugin:

```powershell
python .agents/gen_skill_routes.py --kind gpp --into <project>
python .agents/gen_skill_routes.py --kind windows --into <project>
```

The table routes by the file being changed, not by wording in `AGENTS.md` or by
whether the model happened to request a skill. Every matching row fires, so a
Windows test receives the generic C++ floor, the testing standard, and the
Windows layer. Project `AGENTS.md` files contain only project facts.

`agent-process` from `Concertable/agent-standards` must be installed once in
both Claude Code and Codex; it owns the single shared write hook. `newcpp`
generates the route table automatically. The commands above are for migrating a
manually created or existing repository.

## Authoring

The plain Markdown files under `standards/` are the source of truth. Each
`.agents/skills/*/SKILL.md` is a small router to exactly one document. Generated
Claude skills and installable plugin payloads are never edited directly.

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
python .agents/gen_skill_routes.py --self-test
```

`cpp-standards` and `gpp-standards` are separate plugins deliberately. A Linux
project such as `note-cli` receives the generic C++ base plus the GCC/Linux delta;
a Windows project never receives the Linux delta.
