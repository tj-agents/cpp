# cpp

Read README.md before changing repository structure.

Authored skills live under `.agents/<namespace>/skills/<subject>/SKILL.md`, with
`cpp`, `gpp`, `msvc` and `win32` as the four namespaces. Each skill owns its complete
frontmatter and guidance. Kind is metadata describing its role; subject determines its path.
Learner facts live under `.agents/<namespace>/learning/` and are packaged as data.

`.agents/plugins/payloads.json` declares package sources and resources. Host manifests live
under `.agents/plugins/manifests/`. The Template generator owns `.codex/skills/`,
`.claude/skills/`, `.agents/INDEX.md`, marketplace files and `plugins/*`.
Author shared definitions in their namespace source, then regenerate these outputs.

Scope ownership is strict: `cpp` is platform-neutral C++, `gpp` is the G++/GCC toolchain,
`msvc` is the MSVC/clang-cl toolchain and scaffold, and `win32` is the user-mode Windows API.
Toolchain and API selection are independent. Never infer MSVC from the host OS or Win32 use,
and never make Win32 require one compiler. WDK/kernel guidance remains outside these scopes.

Capability ownership must match the subject named by the capability. Compare a proposed topic
with the skill's name and description; a distinct general pattern with its own trigger earns
its own skill. Mixins, CRTP behavior providers and policy-style composition belong to
`cpp:mixins`. `CLAUDE.md` imports this file.

Shared scaffold templates are authored once under `.agents/cpp/assets/scaffold/templates/`.
Toolchain templates and the Win32 overlay belong to their respective scaffold skills under
`assets/templates/`. `scripts/gen_skill_routes.py --scaffold-assets` materializes shared
resources and route profiles beside those skills before generic package generation.
Scaffold scripts use their own packaged resources. Never hand-edit the materialized copies.

Both host plugin manifests omit release versions. New sessions consume the current publisher main.
Publish only the canonical cpp, gpp, msvc and win32 packages. Retire superseded names and callers
in the same cutover. Use the shared catalog's identity policy for both host catalogs, harness
declarations, SessionStart guidance and scaffold callers.

Run `uv run python -B scripts/gen_skill_routes.py --scaffold-assets`, then
`pwsh .agents/sync-generated.ps1` after authored changes. Before delivery require the scaffold
asset check, generated freshness, route self-test, scoped Python build gate, all repository tests,
both host validators and scaffold acceptance tests, including real builds where toolchains exist.
Keep historical signed provenance unchanged; refresh trusted pins through their owning workflow.

<!-- BEGIN personal:rules sha256:eee7a719bb90e67aaa81ac101a45836dd099bc745fee61216c99ec7d6075f12d -->
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
collaborating developers. Run each migration once during the cutover and delete it; never ship migration
or cleanup code that runs again later. CI fails a commit that removes or renames a skill while a tracked source
still names its old `<package>:<name>`.

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
