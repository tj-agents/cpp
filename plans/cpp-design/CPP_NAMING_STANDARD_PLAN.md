# C++ semantic type naming standard

## Objective

Publish a focused addition to `cpp:style` that names types and concepts for their
meaning, relying on namespace context rather than boilerplate labels.

## Authorization and scope

Tommy authorized this standards-only change on 2026-09-27, including generation,
validation, a local commit, and a personal GitHub pull request. It does not authorize
renaming unrelated project APIs or changing Sandbox HWID or WinWrap.

## Settled policy

- Use the meaningful noun for a type or concept.
- Do not mechanically add `Record`, `Data`, `Model`, `Info`, or similar labels.
- Add a qualifier only when it distinguishes coexisting representations or a real
  responsibility at the use site.
- Consider the owning namespace before repeating its meaning in a type name.
- Keep established names where their qualifiers communicate a real distinction:
  `Identity`, `IdentityRequest`, `winwrap::kernel::driver::Context`,
  `ObjectContext<T>`, and `ContextConfig` are representative examples.

## Work

- [x] Update the authored `cpp:style` semantic-type naming guidance.
- [x] Bump every affected host manifest version, regenerate packages, and record the
      resulting package versions.
- [x] Run the generator, route, hook, marketplace, attester, available host-validator,
      and MSVC scaffold acceptance checks.
- [ ] Re-run the G++ and MinGW Win32 scaffold checks in an environment with a working
      WSL or Git Bash drive mount.
- [x] Review and commit the standards change.
- [x] Push and open the personal GitHub pull request.

## Progress

- 2026-09-27: Created an isolated `Docs/Cpp-Naming-Standard` worktree at main
  `0dcd30a`. The existing style guidance already preserves `Identity` and
  `IdentityRequest`; this change makes the anti-boilerplate rule and established
  distinction examples explicit.
- 2026-09-27: Updated the authored style source, bumped `cpp` from 0.4.4 to
  0.4.5 and `base`/`cpp-standards` from 0.7.4 to 0.7.5 in both host manifests,
  regenerated 299 files from 18 definitions, and recorded all three package
  version hashes. Generator freshness and all six route profiles pass.
- 2026-09-27: Passing checks: canonical names (7), mixins (6), structure (2),
  marketplace (11 plus one documented skip), package versions (3), routes (4),
  hook contract (8), session hooks (11), attester safety (4), and MSVC scaffold
  acceptance (4). Claude validates the regenerated `base`, `cpp`, and
  `cpp-standards` packages; no Codex executable is available for its host validator.
- 2026-09-27: `test_gpp_scaffold.py` is blocked before scaffold generation because
  the configured WSL-backed `g++` has no `/bin/bash`; its 7 tests fail with no
  repository assertion failure. The two G++-dependent Win32 tests fail for the
  same reason, while the MSVC Win32 coverage passes. `test_sync_generated_safety.py`
  has one unrelated failure when Python resolves the temporary root as
  `C:\\Users\\TOMMYS~1\\...` but the test retains its long-path spelling for
  `Path.relative_to`. Re-run these checks after supplying a working Bash drive
  mount and a consistent long-path Python environment; no unrelated test change
  is authorized by this naming-standard delivery.
- 2026-09-27: Reviewed the exact generated and authored diff with a clean
  `git diff --check` and committed `Clarify semantic C++ type naming`.
- 2026-09-27: Pushed `Docs/Cpp-Naming-Standard` and opened
  https://github.com/tj-agents/cpp/pull/30.

## Acceptance criteria

- The authored `cpp:style` source communicates the settled policy without a blanket
  ban on legitimate established names.
- Every generated package affected by the base style payload is fresh and has a
  new recorded version.
- Required checks pass, or any unavailable host-specific check is reported with its
  concrete reason.
- The branch is committed, pushed, and represented by a plain GitHub pull request.
