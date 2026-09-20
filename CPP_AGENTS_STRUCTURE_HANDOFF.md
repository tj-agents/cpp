> **Superseded layout:** P3 implemented the later `.agents/<scope>/<kind>/<name>/SKILL.md`
> correction. This handoff remains historical evidence for the accepted scaffold and logical
> scope split; its physical `standards/*` paths are no longer canonical. See `ARCHITECTURE.md`.

# Handoff: separate toolchains, Win32 APIs and reusable utilities

This is a separate cpp-agents correction handoff. It does not replace the sandbox-hwid
kernel curriculum or its teaching handoff. The user requested the structure below after
rejecting the placement of generic MSVC guidance and scaffolding in the Windows package.

## User decisions to implement

The canonical sections are **base, gpp, msvc and win32**. Every section has a **utility**
group that owns utility skills, with a shared **scripts** directory at that group's root.
Establish the grouping even when no utilities have been implemented for a section yet.

```text
base/
  utility/
    scripts/
gpp/
  utility/
    scripts/
msvc/
  utility/
    scaffold/
      SKILL.md
    scripts/
      New-MsvcProject.ps1
win32/
  utility/
    scripts/
```

This is the required logical hierarchy, not permission to collapse the repository's
authored-source and generated-package trees into one directory. Make the grouping visible
in the authored content and generated package navigation, using supported harness layouts.

| Section | Owns | Utility ownership example |
|---|---|---|
| base | Platform-neutral C++ style, learning, dependencies, testing and build principles | A future tool that is independent of compiler and platform |
| gpp | g++ toolchain guidance and its associated tools | A future g++-specific helper |
| msvc | Generic MSVC compiler, SDK/toolset selection, ABI/runtime and build environment guidance | The existing MSVC project scaffold and its PowerShell helpers |
| win32 | Win32 API design, Unicode, native resources, API errors and applicable WIL/WinWrap guidance | Future utilities whose purpose requires Win32 APIs |

Extract MSVC responsibilities from `windows` first; rename the remaining API section to
`win32`. Use `gpp` as the canonical identity requested by the user; the current repository
calls that package `gcc`, which must be handled as an explicit identity migration.

A plain C++ console application or library built with MSVC selects **base + msvc**.
Add **win32** when the project directly uses those APIs. Targeting Windows, using CMake,
running PowerShell or compiling with MSVC does not alone justify applying Win32 rules.
Likewise, Win32 API guidance must not inherently require the MSVC section; select the
actual toolchain independently. Keep WDK/kernel restrictions in the consuming driver's
scoped guidance rather than imposing them on ordinary MSVC projects.

## The utility convention must be durable

- Establish one shared structural contract in `ARCHITECTURE.md`, with a concise pointer
  from `AGENTS.md`. Do not make future agents infer the arrangement from the scaffold.
- Give every section a documented `utility` group and navigation entry. Empty groups
  should say that no utilities are supplied yet; do not invent helpers or executable skills.
- Utility skill folders live under that group. Their instructions explain when and how
  to invoke the associated scripts in the same group's `scripts/` directory. Multiple
  skills may reuse a helper there without duplicating it. Keep resource paths independent
  of the caller's current directory and verify them after packaging and installation.
- A utility has one owning section, selected by its actual dependencies. Do not copy
  the MSVC scaffold into base, gpp or win32 merely to make the directories look populated.
- Put the scaffold guidance under `standards/msvc/utility/scaffold/` and its executable
  helpers under `standards/msvc/utility/scripts/`. Keep templates under the same utility
  resource tree with explicit ownership and relative references. Adjust the generator's
  source-router mapping as needed; generated packages must preserve usable relative paths.
- Keep the current base source domain `standards/cpp/` mapped explicitly to the public
  `base` section; its utility home is `standards/cpp/utility/`. Use
  `standards/gpp/utility/`, `standards/msvc/utility/` and `standards/win32/utility/`
  for the other sections. Document this mapping once rather than creating duplicate rules.
- `utility` is a category inside a section. The current route generator also uses the word
  `kind` for a project profile; do not accidentally replace project/toolchain selection with
  a utility category. Make that distinction explicit in the source metadata and docs.
- Verify supported Codex/Claude skill discovery and identifiers before choosing packaged
  skill paths. Do not invent manifest fields or assume that arbitrarily nested SKILL.md
  files are discovered. Preserve the requested utility grouping in the authored organization.
- Script language follows the utility's actual platform requirements, not the fact that
  this first utility uses PowerShell. Future gpp utilities must work on **Windows and Linux**.
  Their scripting-language choice and implementation are explicitly deferred; do not copy
  the MSVC PowerShell assumption into gpp or begin a new gpp scaffold during this correction.

## Current state and provenance

Repository: `C:/Users/tommy/source/repos/cpp/windows/cpp-agents`.

Continue the existing work on `docs/generic-msvc-toolchain`; its published implementation
baseline is [`a05e8a3c5cd5a56ae77e89d3c2a2d400a86be16a`](https://github.com/tomjseery/cpp-agents/commit/a05e8a3c5cd5a56ae77e89d3c2a2d400a86be16a).
That commit adds the functional scaffold and generic MSVC standard, but places them in the
wrong section. Preserve useful implementation and tests while correcting ownership.
It is pushed but not merged into main. No PR existed at handoff preparation; recheck live
state before publication. Do not rewrite the already-pushed commit or force-push.

The existing `AGENTS.md`, `ARCHITECTURE.md` and `MIGRATION.md` describe the old combined
Windows ownership. The user's explicit correction above supersedes that structure; update
those files as part of implementing it rather than treating the old rule as a blocker.

Windows plugin 0.5.0 is currently installed from the local source. Its files were generated
and validated, and the scaffold was built as both C++20 and C++23. Those checks establish
existing behavior, not correctness of the rejected organization. The current canonical
packages are base/windows/gcc, with temporary cpp-standards and gpp-standards aliases.
The documented compatibility window currently ends after 2027-03-31.

## Exact surfaces to inspect and change

| Surface | Required correction |
|---|---|
| `AGENTS.md`, `ARCHITECTURE.md`, `README.md`, `MIGRATION.md` | Define four sections, shared utility organization, composition and a safe migration procedure |
| `standards/windows/`, `standards/gcc/`, `standards/cpp/` | Separate generic compiler rules from API rules; create the utility grouping in each owning domain |
| `.agents/skills/` | Update source routers, skill identities, utility classification and paths to shared utility scripts |
| `.agents/plugins/payloads.json`, `.agents/plugins/marketplace.json` | Declare canonical base/gpp/msvc/win32 packages, correct payload ownership and dependencies |
| `.agents/sync-generated.ps1` | Support utility navigation/resources without weakening ownership or generated-drift checks |
| `.agents/gen_skill_routes.py`, `.agents/hooks/session_context.py` | Select toolchains and APIs independently; emit canonical namespaces with explicit compatibility handling |
| `.agents/hooks/tests/test_session_context.py`, `.agents/tests/test_marketplace_contract.py`, generator self-tests | Verify positive and negative composition cases and utility packaging |
| `.github/workflows/ci.yml` | Replace hard-coded old package lists and validate all canonical and temporary compatibility payloads |
| `plugins/`, `.claude/skills/`, generated domain indexes | Regenerate through the supported generator; never hand-edit generated rule copies |

The generator currently scans flat source router directories, requires one router for each
non-index standards document, and copies resources by source domain. Design utility indexes
and nested resource paths around explicit tested contracts; an extra README can otherwise
become an orphan document. The current route/hook constants hard-code windows/gcc and even
normalize gpp to gcc. A directory rename alone will leave those behaviors wrong.

Preserve the pinned external `concertable:*` workflow contract. This correction concerns
technical-section ownership and does not require replacing the external workflow provider.
If changes do touch that contract or its trust path, follow the repository's existing
provenance requirements rather than bypassing them.

## Migration and verification

1. Inspect the current branch, remotes, installed packages and consumer references. Preserve
   local changes. Do not assume the state recorded above has remained unchanged.
2. Implement the ownership split and uniform utility layout in authored sources. Retain
   useful scaffold behavior; avoid unrelated language/style rewrites.
3. Update the generator, routing, manifests and regression tests together. Define any
   temporary compatibility packages and old-name input mappings explicitly. Never silently
   reinterpret every old `windows` consumer as needing just one half of the split.
4. Regenerate both harness payloads. Check utility-skill discovery and invocation of the
   shared scripts from an unrelated working directory. Validate the packaged scaffold as well as its
   source form, including C++20/23 builds, paths with spaces, `-WhatIf`, configuration copying
   and refusing an existing destination.
5. Run the repository's mandatory generation, route, hook and marketplace tests, then both
   harness validators for every package. Add meaningful assertions for the new structure.
6. Use supported installation/update commands to verify new identities and skill resolution.
   Preserve local cache changes and install replacements before removing old packages.
   Document consumer migration and check known consumers rather than deleting old names blindly.
7. Commit the correction as forward changes and push a verified branch. Merging remains a
   separate operation. Report package versions, installed state, remaining compatibility
   references and the exact remote commit; do not equate a push with a default-branch release.

The required routing evidence includes a generic project selecting base only, an MSVC
console/library project selecting base + msvc without Win32, a g++ project selecting
base + gpp, and a Win32 consumer adding win32 to its chosen toolchain. All four sections
must expose the utility grouping; only MSVC owns the existing scaffold. Newly emitted routes
must not use windows/gcc namespaces except inside explicit legacy compatibility payloads.

Keep the sandbox-hwid source, driver-loading state and kernel teaching plan separate. Audit
its existing windows skill references as a consumer migration concern; no kernel code or
machine setup change is part of this structural correction. WinWrap implementation work
also remains a later task; future usage guidance belongs in win32.

## Completion criterion

The authored source, generated packages, documented hierarchy, routing, tests and installed
skill resolution all agree on base/gpp/msvc/win32 with a utility group in every section.
Each group has a defined home for utility skills and their shared scripts. The reusable
MSVC scaffold resolves and runs its packaged script correctly, and selecting MSVC alone
does not activate Win32 API conventions. The correction handoff can then be retired in
favor of the canonical architecture and migration documentation.
