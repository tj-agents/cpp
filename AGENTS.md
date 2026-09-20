# cpp-agents

Read README.md before changing repository structure.

Authored capabilities live only under `.agents/base/<kind>/<name>/`,
`.agents/gpp/<kind>/<name>/`, `.agents/msvc/<kind>/<name>/`, and
`.agents/win32/<kind>/<name>/`. Each capability owns its complete `SKILL.md` body there.
Do not restore a separate `standards/` source tree or author shared definitions in `.codex/`,
`.claude/`, `.agents/skills/`, or `plugins/`.

`.agents/plugins/sources.json` owns the source/package map and generated-root declaration.
`.agents/skills/`, `.codex/skills/`, `.claude/skills/`, `.agents/*/INDEX.md`, marketplace
files, and `plugins/*` are generated. Authored host manifests live under
`.agents/plugins/manifests/`. Run `pwsh .agents/sync-generated.ps1` after authored changes
and require `pwsh .agents/sync-generated.ps1 -Check` before delivery.

Scope ownership is strict: `base` is platform-neutral C++, `gpp` is the G++/GCC toolchain,
`msvc` is the MSVC/clang-cl toolchain and scaffold, and `win32` is the user-mode Windows API.
Toolchain and API selection are independent. Never infer MSVC from the host OS or Win32 use,
and never make Win32 require one compiler. WDK/kernel guidance remains outside these scopes.

Every scope has a documented `utility/` and `utility/scripts/` home. Empty homes state that no
utilities exist. Repository-owned runtime resources ship inside their owning plugin; the MSVC
scaffold resources are mapped explicitly by `.agents/plugins/sources.json`.

`base`, `gcc`, `windows`, `cpp-standards`, and `gpp-standards` are generated compatibility
packages only. Preserve their 2027-03-31 window and keep the old combined `windows` payload
containing both MSVC and Win32; never map it silently to only one new scope.

Required validation is the generator check, route self-test, hook tests, marketplace and
attester tests, both host validators when available, and the MSVC scaffold acceptance matrix.
Keep historical signed provenance unchanged.
