# Concertable source attestation

This directory is immutable verification evidence, not a second source of workflow standards. It proves that the external skill identifiers used by `cpp-agents` exist in the pinned, GitHub-signed `Concertable/agent-standards` commit without requiring CI access to that private repository.

`commit.txt` carries the Git commit object body; its text-file newline is removed according to the explicit provenance flag before hashing. `github-web-flow.asc` is GitHub's published web-flow signing key from `https://github.com/web-flow.gpg`. `provenance.json` records the signed tree path down to the manifest and required skill files. `plugin.json` and `skills/*/SKILL.md` are inert source snapshots: CI hashes them back to their signed Git blobs, validates their metadata, and never loads them as standards.

GitHub's web-flow key is shared across repositories, so the offline signature alone does not assert repository ownership. The release-time live-source gate queries GitHub's authenticated repository API for the pinned object and verifies the checkout's `origin` before this attestation can change; subsequent CI proves that the reviewed evidence remains byte-for-byte unchanged.
