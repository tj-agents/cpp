# Technical debt

## Enforce the provenance gate through branch protection

`External contract provenance / repository-binding` is an automated, trusted exact-head check, but GitHub
does not allow this private repository's current account plan to configure branch protection or repository
rulesets. Until that capability is available, maintainers must treat a green provenance check as a manual
merge precondition for every protected trust-contract change.

Resolve this entry when the repository becomes public or its account gains private-repository rulesets:
require `External contract provenance / repository-binding` on `main`, require branches to be up to date,
verify a protected test PR cannot merge while that check is red, then delete this entry.

## Upgrade the GitHub checkout action without weakening provenance

CI and the trusted attester workflows still use `actions/checkout@v4`, which GitHub currently runs through
its Node 24 compatibility path and annotates as a Node 20 deprecation. Because the trusted workflow and its
safety test are pinned inside the provenance closure, upgrade all checkout uses only through a reviewed
trust-root rotation. Resolve this entry when the chosen supported checkout major passes ordinary CI and the
Ubuntu/Windows attester-safety matrix, the new exact workflow blobs are pinned, and the deprecation
annotation is absent.

## Generated skill discovery flattens the kind hierarchy

`.codex/skills/` and `.claude/skills/` place every generated `SKILL.md`
pointer at `<root>/<name>/SKILL.md`, one flat level, regardless of that skill's `kind`
(`contract`, `knowledge`, `utility`) or domain scope. A `utility` adapter such as `gpp-scaffold`
or `msvc-scaffold` looks identical in that flat listing to a `contract` like `cpp-build` — the
kind is only visible by opening the file and reading its frontmatter, or by following it back
to the authored `.agents/<scope>/<kind>/<name>/` tree. This reads as disorganized when scanning
the generated directories directly and expecting them to reflect the authored kind taxonomy.

Resolve this entry by first checking whether Claude Code's and Codex's skill-discovery contracts
actually require `<skills-root>/<name>/SKILL.md` with no deeper nesting, or whether they tolerate
`<skills-root>/<kind>/<name>/SKILL.md`; if nesting is safe, update `sync-generated.ps1` and
`sources.json`'s adapter-root handling to emit it that way. If a host can't support that, resolve
this instead by rendering `kind` into the pointer stub's heading (e.g. `# gpp-scaffold (utility)`)
so the distinction survives a flat listing, then delete this entry.
