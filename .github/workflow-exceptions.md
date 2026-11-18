# Workflow exceptions

Each zizmor exception names one exact rule, workflow, line and column.
Job naming exceptions in `workflow-baseline.json` preserve published check contexts.

| Rule | Location | Reason |
| --- | --- | --- |
| `adhoc-packages` | `ci.yml:40:14` | The host acceptance test intentionally installs the two explicitly version-pinned native CLIs in this exact step. |
| `dangerous-triggers` | `provenance-gate.yml:4:3` | The provenance checker checks out the trusted PR base, validates canonical PR identity, and reads untrusted Git objects only as data; it never executes PR code. |
| `undocumented-permissions` | `provenance-gate.yml:9:3` | Tommy forbids explanatory code comments. The exact permission grants the named qualification, status-reading or release-publication job its required API access. |
| `dangerous-triggers` | `update-provenance-pins.yml:4:3` | Only canonical own-repository PRs are eligible; the workflow checks out main and runs its trusted isolated proposal script, which treats the consumer Git objects as data. |
| `undocumented-permissions` | `update-provenance-pins.yml:15:3` | Tommy forbids explanatory code comments. The exact permission grants the named qualification, status-reading or release-publication job its required API access. |
