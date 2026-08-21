# C++ standards delivery

The split is by audience:

```text
Linux C++ project   -> cpp-standards + gpp-standards
Windows C++ project -> cpp-standards + windows-standards
One project          -> its own AGENTS.md for project-only facts
                      + generated .agents/skill-routes.json
```

`cpp-standards` and `gpp-standards` share this marketplace because the latter is
the toolchain delta for the generic C++ corpus. Windows-native guidance has its
own repository and marketplace because it is a substantial platform discipline
with an independent project set.

A rule has one authored home under `standards/<domain>/`. A router skill owns one
document. `.agents/sync-generated.ps1` copies the applicable documents and
rewritten routers into each self-contained plugin, generates Claude manifests
from the canonical Codex manifests, and fails if a document, router, plugin, or
payload mapping is orphaned.

The session hook is mechanism rather than rule text. It detects a C++ checkout
and tells the agent which installed skills apply. The generated route table's
explicit project kind wins over the host platform, so a GPP project still loads
its Linux toolchain guidance when inspected from Windows and a Windows project
never inherits GPP guidance merely because an agent runs on Linux. The hook is
bundled once, in `cpp-standards`, so installing both C++ plugins never registers
duplicate hooks.

Write-time enforcement reuses the `agent-process` plugin's router—the same hook
Concertable uses. `.agents/gen_skill_routes.py` derives a per-repository table
for `portable`, `gpp`, or `windows`; the table contains routing data, never a copy
of a standard. This keeps the hook implementation in one plugin and the C++
mapping in its owning marketplace.

No consumer imports a parent directory. Plugin caches are self-contained, and a
project's `AGENTS.md` contains only facts unique to that project.
