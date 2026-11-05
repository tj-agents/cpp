# Architecture

## Source ownership

`.agents/` is the sole host-neutral source. A capability's complete frontmatter and guidance
live together at `.agents/<scope>/<kind>/<name>/SKILL.md`. The four scopes are:

- `base`: platform-neutral C++ contracts and knowledge, published as `cpp`;
- `gpp`: the G++/GCC toolchain, published as `gpp`;
- `msvc`: the MSVC/clang-cl toolchain and scaffold utility, published as `msvc`;
- `win32`: user-mode Windows API contracts, knowledge and the GUI application overlay, published as `win32`.

This layout supersedes the physical `standards/*` paths recorded in
`CPP_AGENTS_STRUCTURE_HANDOFF.md` while retaining its useful logical separation and scaffold.
`.codex/` and `.claude/` contain generated host discovery entries only. `plugins/*` is generated
distribution output. `.agents/plugins/manifests/` is the authored host-manifest source.

Each scope has `utility/` and `utility/scripts/`. Empty groups say that no utility exists. The
G++ and MSVC scaffolds own their toolchain templates under `.agents/<scope>/utility/scripts/`
and layer the platform-neutral templates owned by `.agents/base/utility/scripts/templates/`
underneath; a toolchain template at the same path wins. `win32:scaffold` is an overlay that
converts either result's `app` target into a Win32 GUI application without choosing a
compiler. Package resource mapping is explicit in `sources.json`: every package receives the
resources it runs, so no package depends on another installation.


Capability identity is the pair of plugin and name, such as `cpp:style` or `win32:style`.
Authored directories and canonical plugin payloads use the short name. Flat host discovery
roots need globally distinct directory names, so `sources.json` explicitly maps them to
names such as `cpp-style` and `win32-style`. Those adapter filenames are not redundant
plugin-qualified identifiers. Package compatibility names are mapped separately.

## Selection model

Every project receives `cpp`. It may select one toolchain (`gpp` or `msvc`) and zero or more API
layers (`win32`) by installing the corresponding plugin. Win32 markers may produce a suggestion,
but detection never applies an API or compiler. MSVC alone does not select Win32, a Windows host
does not select MSVC, and Win32 does not require MSVC.

## Canonical selection

Only cpp, gpp, msvc, and win32 are published. Select compiler and API layers explicitly; the generator does not retain aliases for superseded identifiers.

WDK and kernel capabilities remain outside this user-mode architecture until separately validated.
