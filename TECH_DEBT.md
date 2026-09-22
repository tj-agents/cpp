# Technical debt

## Review provenance pins for the canonical capability migration

The canonical capability migration changes `.agents/tests/test_marketplace_contract.py`
and `.github/workflows/ci.yml`, both protected by the trusted attester on `main`.
Their candidate blobs (`146855dd6374481f8892bc10a5db950f8d3ed8a5` and
`df7e24389ccad14c333e93de7fc6eb1abc7dc9c4`) differ from the separately reviewed pins
(`004c73dc421ed64a71563140b62b4f624f5bec7e` and
`0e15c93383f209a28dde4b034b5a7754ac74c560`). The existing repository-binding failure
reports the absent exact-head attestation; the current trusted script would also reject
these changed objects. Ordinary test success does not satisfy this review requirement.

Resolve through a separately reviewed update of the trusted pins on canonical `main`,
then run that trusted attester against the full candidate SHA and rerun repository-binding.
Delete this entry when the reviewed objects match and the exact candidate's provenance
gate passes. Keep historical signed evidence unchanged and do not manufacture a success
status or weaken the gate to deliver a design-guidance change.

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
