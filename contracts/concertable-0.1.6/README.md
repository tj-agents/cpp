# Concertable source attestation

This directory is immutable verification evidence, not a second source of workflow standards. It proves that the external skill identifiers used by `cpp-agents` exist in the pinned, GitHub-signed `Concertable/agent-standards` commit without requiring CI access to that private repository.

`commit.txt` carries the Git commit object body; its text-file newline is removed according to the explicit provenance flag before hashing. `github-web-flow.asc` is GitHub's published web-flow signing key from `https://github.com/web-flow.gpg`. `provenance.json` records the signed tree path down to the manifest and required skill files. `plugin.json` is the only source payload copied here, so CI can independently verify the external plugin identity, version, and repository.
