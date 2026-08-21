# cpp-agents

Tommy's reusable C++ standards for Claude Code and Codex. The repository is an
installable marketplace, so consuming projects do not depend on where this repo
or the project is cloned.

## Plugins

| Plugin | Install where | Scope |
|---|---|---|
| `cpp-standards` | Every C++ machine | Platform-neutral style, libraries, learning workflow, direction, and current knowledge |
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

## Authoring

The plain Markdown files under `standards/` are the source of truth. Each
`.agents/skills/*/SKILL.md` is a small router to exactly one document. Generated
Claude skills and installable plugin payloads are never edited directly.

```powershell
pwsh .agents/sync-generated.ps1
pwsh .agents/sync-generated.ps1 -Check
```

`cpp-standards` and `gpp-standards` are separate plugins deliberately. A Linux
project such as `note-cli` receives the generic C++ base plus the GCC/Linux delta;
a Windows project never receives the Linux delta.
