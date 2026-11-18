# Architecture

## Source ownership

`.agents/` is the host-neutral source. Each skill's complete frontmatter and guidance lives
at `.agents/<namespace>/skills/<subject>/SKILL.md`. The four namespaces are:

- `cpp`: platform-neutral C++ standards, learning guidance and learner data;
- `gpp`: the G++/GCC toolchain and scaffold;
- `msvc`: the MSVC/clang-cl toolchain and scaffold;
- `win32`: user-mode Windows API guidance, learner data and the GUI application overlay.

Kind describes a skill's role independently of its directory. Learner facts and progress are
plain data under `learning/`. `.agents/plugins/payloads.json` declares package sources and
resources; `.agents/plugins/manifests/` owns authored host manifests. The vendored Template
generator produces host discovery entries, the shared index, marketplace files and plugin packages.

Shared scaffold templates have one authored home: `.agents/cpp/assets/scaffold/templates/`.
Toolchain templates and the Win32 overlay live in their scaffold skill's `assets/templates/`.
The repository's `scripts/gen_skill_routes.py --scaffold-assets` materializes shared templates
under each scaffold skill's `assets/shared/templates/` and renders its route profiles. Generic
package generation then copies these complete skill resources into each host package.

A scaffold uses its own adjacent resources in source, native discovery and standalone plugin
layouts. A toolchain template at a matching path wins over the shared template. `win32:scaffold`
converts either toolchain's `app` target into a GUI application without selecting a compiler.
The scaffold asset check verifies materialized resources against their authored source.

Capability identity is plugin plus subject, such as `cpp:style` or `win32:style`. Canonical
packages retain subject paths. Flat host discovery directories use distinct generated names
such as `cpp-style` and `win32-style`.

## Selection model

Every C++ project receives `cpp`. It may select one toolchain (`gpp` or `msvc`) and API
layers such as `win32`. Route profiles record these dimensions independently. Win32 markers
may suggest an API when no profile exists, but detection never applies an API or compiler.
MSVC alone does not select Win32; the host operating system does not select a toolchain.

Generated routes contain technical skills only. Engineering workflows are independently owned
and installed. Historical signed contract evidence remains immutable and does not add a new
route dependency.

## Canonical selection

Only cpp, gpp, msvc and win32 are published. Select compiler and API layers explicitly.
WDK and kernel capabilities remain outside this user-mode architecture until separately validated.
