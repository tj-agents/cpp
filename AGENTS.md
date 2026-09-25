# cpp

Read README.md before changing repository structure.

Authored capabilities live only under `.agents/base/<kind>/<name>/`,
`.agents/gpp/<kind>/<name>/`, `.agents/msvc/<kind>/<name>/`, and
`.agents/win32/<kind>/<name>/`. Each capability owns its complete `SKILL.md` body there.
Do not restore a separate `standards/` source tree or author shared definitions in `.codex/`,
`.claude/`, `.agents/skills/`, or `plugins/`.

`.agents/plugins/sources.json` owns the source/package map and generated-root declaration.
`.codex/skills/`, `.claude/skills/`, `.agents/*/INDEX.md`, marketplace files, and `plugins/*`
are generated. `.agents/skills/` must not exist: `.agents/` is the sole canonical shared tree.
Authored host manifests live under
`.agents/plugins/manifests/`. Run `pwsh .agents/sync-generated.ps1` after authored changes
and require `pwsh .agents/sync-generated.ps1 -Check` before delivery.

Scope ownership is strict: `base` is platform-neutral C++, `gpp` is the G++/GCC toolchain,
`msvc` is the MSVC/clang-cl toolchain and scaffold, and `win32` is the user-mode Windows API.
Toolchain and API selection are independent. Never infer MSVC from the host OS or Win32 use,
and never make Win32 require one compiler. WDK/kernel guidance remains outside these scopes.

Capability ownership must match the subject named by the capability, not merely a nearby
design concern or an example that happens to use it. Before adding guidance to an existing
skill, compare the topic with that skill's name and description; when the topic is a distinct
general pattern with its own trigger, give it its own capability. In particular, mixins,
CRTP behavior providers, and policy-style composition belong to `cpp:mixins`, never
`cpp:domain-design`. `CLAUDE.md` imports this file, so do not duplicate this rule there.

Every scope has a documented `utility/` and `utility/scripts/` home. Empty homes state that no
utilities exist. Repository-owned runtime resources ship inside every plugin that uses them, as
mapped explicitly by `.agents/plugins/sources.json`: shared scaffold templates are owned by
`.agents/base/utility/scripts/`, toolchain templates by `gpp`/`msvc`, the Win32 GUI overlay by
`win32`, and scaffold route profiles are rendered by the route generator, never hand-written.

Any change to a generated package's content needs a new version in both of its host manifests.
After regenerating, run `python .agents/sync_generated.py --record-package-versions`; the
append-only `.agents/plugins/package-versions.json` fails the tests if content changes under a
recorded version.

`base`, `gcc`, `windows`, `cpp-standards`, and `gpp-standards` are generated compatibility
packages only. Preserve their 2027-03-31 window and keep the old combined `windows` payload
containing both MSVC and Win32; never map it silently to only one new scope.

Required validation is the generator check, route self-test, hook tests, marketplace and
attester tests, the package-version record, both host validators when available, and the
G++, MSVC and Win32 scaffold acceptance tests (real builds where the toolchains exist).
Keep historical signed provenance unchanged.
