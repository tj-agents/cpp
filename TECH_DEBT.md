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
