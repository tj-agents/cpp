# Technical debt

## Enforce the provenance gate through branch protection

`External contract provenance / repository-binding` is an automated, trusted exact-head check, but GitHub
does not allow this private repository's current account plan to configure branch protection or repository
rulesets. Until that capability is available, maintainers must treat a green provenance check as a manual
merge precondition for every protected trust-contract change.

Resolve this entry when the repository becomes public or its account gains private-repository rulesets:
require `External contract provenance / repository-binding` on `main`, require branches to be up to date,
verify a protected test PR cannot merge while that check is red, then delete this entry.
