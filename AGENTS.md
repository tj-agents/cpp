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

Both host plugin manifests omit release versions. New sessions consume the current publisher main.
Regenerate packages after changing authored source.

Publish only the canonical cpp, gpp, msvc, and win32 packages. Do not add compatibility
packages, aliases, or fallback selectors.
Use the [shared catalog's identity policy](https://github.com/tj-agents/marketplace#readme)
for both host catalogs, harness declarations, SessionStart guidance and scaffold callers.

Required validation is the generator check, route self-test, hook tests, marketplace and
attester tests, both host validators when available, and the
G++, MSVC and Win32 scaffold acceptance tests (real builds where the toolchains exist).
Keep historical signed provenance unchanged.

<!-- BEGIN personal:rules sha256:f878befe2d5e1e69bc6e5cc2ed10c6e684ce894987ff4a9861c7cc2b802fe802 -->
# Personal rules

These rules govern every project that explicitly adopts `personal@tj-agents`. Adoption records the
project's personal scope; a home directory, author name or employer association never establishes it, and
employer projects stay outside this profile unless the user explicitly extends that scope. Before planning
or starting work, confirm the task is clear against each rule below.

## 1. Clean cut

Keep one current supported solution. When replacing behavior, remove the superseded names, aliases,
fallback implementations, adapters, configuration formats, compatibility branches and forwarding or
migration docs. Migrate all known callers, project declarations, installed registrations, generated
artifacts and live runtime entry points in the same cutover, and coordinate upgrades with the actual
collaborating developers. A commit that removes or renames a skill while a tracked source still names its
old `<package>:<name>` is blocked until every reference is migrated or deleted.

Verify the entry points people actually use on every supported platform, including Windows and Linux
launch paths where supported. Source edits, successful generation, passing unit tests and version commands
alone leave a migration unproven; check installed bindings and fresh runtime behavior. Record any
unverified entry point as incomplete, with its resolver and observable acceptance condition.

```text
Replace old-launch with launch:
1. Migrate the registered shell command, configuration and actual callers.
2. Delete the old entry and regenerate installed settings.
3. Invoke launch from a fresh supported Windows/Linux session and check its actual behavior.
Result: launch --version alone leaves this migration incomplete.
```

A backwards-compatibility exception exists only as an explicit user requirement. Surface it as a
deliberate policy decision, identify the affected supported behavior and reconcile this profile's scope
before implementing it, keeping the exception visible rather than inside a fallback or adapter.

## 2. Proportionate implementation

Solve the demonstrated problem with the smallest suitable implementation. Add abstractions, dependencies,
configuration switches, duplicate paths or process machinery only for a concrete current need. Prefer the
capabilities the project already selects. Verify the behavior and meaningful failure paths in proportion
to the change, with tests that prove behavior rather than restate the implementation.

## 3. Plans

Track work as a GitHub issue or project item. A plan committed under `plans/` is only the detailed
implementation plan behind one such item and links to it; working plans stay machine-local.

This policy is authored once here. A selecting project receives it at SessionStart, and adoption generates
its marked native instruction block from this body and checks it for drift. A selected plugin or an
`always` tier alone is not proof of loading.
<!-- END personal:rules -->
