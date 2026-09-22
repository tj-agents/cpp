# Architecture

## Source ownership

`.agents/` is the sole host-neutral source. A capability's complete frontmatter and guidance
live together at `.agents/<scope>/<kind>/<name>/SKILL.md`. The four scopes are:

- `base`: platform-neutral C++ contracts and knowledge, published as `cpp`;
- `gpp`: the G++/GCC toolchain, published as `gpp`;
- `msvc`: the MSVC/clang-cl toolchain and scaffold utility, published as `msvc`;
- `win32`: user-mode Windows API contracts and knowledge, published as `win32`.

This layout supersedes the physical `standards/*` paths recorded in
`CPP_AGENTS_STRUCTURE_HANDOFF.md` while retaining its useful logical separation and scaffold.
`.codex/` and `.claude/` contain generated host discovery entries only. `plugins/*` is generated
distribution output. `.agents/plugins/manifests/` is the authored host-manifest source.

Each scope has `utility/` and `utility/scripts/`. Empty groups say that no utility exists.
The G++ and MSVC scaffolds own scripts/templates under their respective scope's
`utility/scripts/`. Package resource mapping is explicit in `sources.json`.

Capability identity is the pair of plugin and name, such as `cpp:style` or `win32:style`.
Authored directories and canonical plugin payloads use the short name. Flat host discovery
roots need globally distinct directory names, so `sources.json` explicitly maps them to
names such as `cpp-style` and `win32-style`. Those adapter filenames are not redundant
plugin-qualified identifiers. Package compatibility names are mapped separately.

## Selection model

Every project receives `cpp`. It may select one toolchain (`gpp` or `msvc`) and zero or more API
layers (`win32`). The route profile records these dimensions separately. Win32 markers may produce
a suggestion when no profile exists, but detection never applies an API or compiler. MSVC alone
does not select Win32, a Windows host does not select MSVC, and Win32 does not require MSVC.

Generated routes contain technical skills only. Engineering workflows are independently owned and
installed; this repository retains immutable provenance evidence for the historical external
contract without making it a compulsory new-route dependency.

## Compatibility

`base -> cpp` and `gcc -> gpp` are explicit package/selector migrations. `cpp-standards` and
`gpp-standards` remain aliases through 2027-03-31. Because old `windows` combined compiler and API
assumptions, its compatibility package contains both `msvc` and `win32` payloads. It must never be
mapped automatically to only one replacement.

Canonical packages also retain generated redirects for their previously published redundant
names until 2027-03-31. Compatibility packages keep their original capability names and
rewritten internal references. All bodies originate in the same short-name authored source.

WDK and kernel capabilities remain outside this user-mode architecture until separately validated.
