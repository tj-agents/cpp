# C++ workspace reconciliation plan

Reconcile every still-current reusable C++ capability and scaffold from the older
`tomjseery/cpp` workspace (`C:\Users\tommy\source\repos\cpp`, main `9b3252e`) into the
canonical `tj-agents/cpp` marketplace, release it, and migrate the old workspace and other
active consumers onto the release. `.agents/` stays the only authored source; generated
host adapters, packages and routes are regenerated, never hand-edited.

## Constraints

- The old workspace's normal checkout keeps its user-owned dirty `NORTH_STAR.md` edit
  exactly. Never reset, stash, commit or overwrite it; migrate through a separate worktree.
- Nested repositories under the old workspace's `gpp/` and `windows/` are independent and
  are never copied wholesale.
- Package names `cpp`, `gpp`, `msvc`, `win32` and PR #13's concise capability names are
  canonical. Legacy `base`, `gcc`, `windows`, `cpp-standards` and `gpp-standards` packages
  remain generated compatibility packages through 2027-03-31.
- Toolchain and API selection stay independent. WDK/kernel guidance stays out of scope.

## Stage 0 — priority gate: land PR #13 and adopt it in sandbox-hwid

Requested before the wider reconciliation.

- [x] PR #13 (`fix/explicit-wire-integer-types`) branched from the same base
  (`32610e9`). Its local-ahead commit `1fe4183` only recorded the completed delivery in
  `plans/cpp-design/CPP_DESIGN_STANDARDS_PLAN.md`; it was fast-forward pushed (no force) so
  the branch history lands intact.
- [x] Exact-head CI, attester safety (Ubuntu/Windows) and repository-binding green on
  `1fe4183`; merged as `c718b7654d469884b62aa0b5b20cdefa34f3d83a`.
- [x] Release preparation (`Release/v0.2.0`): PR #13 changed every compatibility package's
  content without bumping versions, and compatibility packages leaked canonical identifiers
  for scopes outside their own (for example `msvc:scaffold` in `gcc`). Completed each
  compatibility package's identifier map, removed the qualified name from the copied G++
  scripts README, restored the canonical packages' `repository` URL (`tj-agents/cpp`,
  regressed by #13), added regression tests for both, bumped `base`/`cpp-standards` 0.5.0,
  `gcc`/`gpp-standards` 0.4.2, `windows` 0.7.0, and promoted the changelog to v0.2.0.
- [x] Release PR [#16](https://github.com/tj-agents/cpp/pull/16) opened; exact-head CI,
  attester safety and repository-binding green on `225a2ad`; independent review found no
  defects (notes: `windows` minor bump is deliberate for new Win32 guidance; widen the leak
  test to scripts — done in Stage 2).
- [ ] **Blocked on user approval:** merging #16 was denied by the session's permission
  classifier ("Merge Without Review"). Resume when the user merges #16 or allows the merge;
  then publish immutable release `v0.2.0` from the merge commit.
- [ ] `sandbox-hwid` adoption: refresh the Claude `cpp-agents` marketplace, install
  `cpp`/`msvc`/`win32@cpp-agents`, disable `base`/`gcc`/`windows@cpp-agents`, remove the
  local marketplace override from `.codex/config.toml`, regenerate
  `.agents/skill-routes.json` from the release if it differs, and confirm a new Claude
  session can write a C++ file without a skill-router block.

## Stage 1 — inventory (old workspace vs canonical at `c718b76`)

| Candidate (old workspace) | Owner | Canonical state | Decision |
|---|---|---|---|
| `NORTH_STAR.md` goal, skill tree, learning rule | `cpp:direction` | Present; compiler/debugger/profiler rows defer to the toolchain | Keep canonical. The gpp picks (GCC, gdb, perf) live in `gpp:toolchain`; `msvc:toolchain` lacks its picks — add the MSVC debugger used by the scaffold and state that no profiler is chosen. Workspace file keeps the user's dirty edit; not rewritten by this migration. |
| `WHAT_I_KNOW.md`, `CODE_CONVENTIONS.md`, `LIBRARY_CONVENTIONS.md`, `windows/*.md` pointers | workspace | Pointers name `tomjseery/cpp-agents` and legacy `base:`/`windows:` identifiers | Workspace migration: point to `tj-agents/cpp` and canonical identifiers. |
| `ARCHITECTURE.md` (layout, CMake conventions, presets, tooling, install) | `cpp:structure`, `cpp:build`, scaffolds | Layout and target rules present; option-carrier sanitizers, `gdb` preset, tooling configs and install rule absent from scaffolds | Port the reusable behavior into the scaffolds; workspace file becomes a pointer. |
| `newcpp` sanitizer option carrier (`<project>_sanitize`, `-D<PROJECT>_SANITIZE`) | `gpp:scaffold`, `msvc:scaffold` | G++ preset sets sanitizers through global `CMAKE_CXX_FLAGS`, contradicting `cpp:build`; MSVC has none | Target-scoped carrier in both; G++ `dev` enables it, MSVC keeps it opt-in. |
| `newcpp` `gdb` preset (Debug, no sanitizers) | `gpp:scaffold` | Absent | Add. |
| `.clang-tidy` `-portability-avoid-pragma-once`, `AllowPointerConditions` | `cpp` (shared config) | Absent from G++ template; MSVC ships none | One canonical formatter/analysis config owned by `cpp`, shipped with both toolchain packages; MSVC keeps its explicit override. |
| `.clangd` removal of GCC module flags | toolchain root CMake | Workaround only fixed clangd; clang-tidy still failed on the flags | Superseded: `CMAKE_CXX_SCAN_FOR_MODULES OFF` until a project adopts modules fixes clangd and clang-tidy. |
| `.editorconfig`, `.vscode/settings.json` (clangd) | `cpp` (shared config) | Absent | Shared template. |
| `.vscode/launch.json` gdb / cppvsdbg | `gpp:scaffold` / `msvc:scaffold` | Absent | Add per toolchain. |
| Install to an on-PATH directory | scaffolds (shared app template) | Absent | Add to both. |
| Project `AGENTS.md` / `CLAUDE.md` | scaffolds | Absent | Add project-facts stubs. |
| `.agents/skill-routes.json` snapshots in `dotfiles/skill-routes/` | generator | Stale legacy snapshots | Delete; the wrapper generates routes with the released generator for the selected composition. |
| `newcpp -Windows` GUI app (wWinMain, manifest, Win32 libs, tidy carve-outs, clangd index) | `win32` utility (toolchain-independent overlay) | Absent; `msvc:scaffold` is console-only by design | New `win32:scaffold` overlay applied to a freshly generated `gpp` or `msvc` project. Static CRT stays an MSVC deployment decision, not a Win32 default. |
| `dotfiles/newcpp.ps1` | workspace | Duplicates templates | Workspace wrapper over the released scaffolds with personal defaults (`git init`, destination). |
| `dotfiles/claude-global.md` | workspace | Names `base@`/`gcc@cpp-agents` | Workspace migration to `cpp` + explicit toolchain. |
| Root `.agents/skill-routes.json` | workspace | Legacy `base:` routes | Regenerate with the released generator (`cpp` only). |

Active consumers found (route profiles naming C++ skills): old workspace root,
`cpp/gpp/note-cli`, `cpp/windows/icon-dropper`, `cpp/windows/wifi-toggle`,
`cpp/windows/winwrap` (legacy identifiers), and `sandbox-hwid` (canonical identifiers).
Compatibility aliases therefore stay through 2027-03-31.

## Stage 2 — implementation (branch `Refactor/ReconcileCppWorkspace`)

- [x] Shared `cpp` templates under `.agents/base/utility/scripts/templates/`, shipped to
  `gpp`, `msvc`, `win32` and the compatibility packages that run them; duplicated G++/MSVC
  sources removed.
- [x] G++ parity (sanitizer carrier, `gdb` preset, configs, launch, install, project notes);
  MSVC parity (opt-in ASan carrier and `asan` preset selecting the ASan component, configs,
  `cppvsdbg`, install, project notes); `win32:scaffold` overlay (`Add-Win32App.ps1`).
- [x] Route profiles rendered by the generator into canonical packages only.
- [x] `msvc:toolchain` skill-tree picks; learning/structure/scaffold/README/ARCHITECTURE/AGENTS.
- [x] Package-version guard: `package-versions.json` + `test_package_versions.py`; debt
  entry deleted. Versions: `cpp`/`gpp`/`msvc`/`win32` 0.3.0, `base`/`cpp-standards` 0.6.0,
  `gcc`/`gpp-standards` 0.5.0, `windows` 0.8.0.
- [x] Generator current (289 files / 17 definitions), route self-test, 11 hook tests,
  63 source tests (1 optional skip), Claude validation of marketplace + nine packages,
  isolated Codex install of all nine, scaffolds run from installed copies. Real builds:
  `cpp+gpp` MinGW (`gdb`, Catch2 tests pass), `cpp+msvc` (`dev` and `asan`, Catch2 tests
  pass), `cpp+msvc+win32` and `cpp+gpp+win32` GUI builds (PE subsystem GUI, manifest
  embedded), clang-tidy clean on console and Win32 sources. The G++ sanitizer `dev` preset
  is not yet built anywhere: CI has no Ninja and `ci.yml` is trust-pinned; Docker and WSL
  compilers are unavailable here. Recorded in `TECH_DEBT.md`.
- [x] CI run 1 on #17 failed: the repository `.gitignore` ignored every `.vscode/`, so the
  scaffold `.vscode` templates were never committed. Anchored the ignores to the root and
  added a test that no authored or generated file is git-ignored.
- [ ] Independent review, fixes, incremental review; PR, green exact-head CI, merge,
  release.

## Stage 3 — consumer migration

- [x] Old workspace prepared in its own worktree
  (`C:\Users\tommy\source\repos\cpp\.worktrees\AdoptCanonicalCppAgents`, branch
  `Refactor/AdoptCanonicalCppAgents`, local commit `1c4e00a`, not pushed): `newcpp` is a
  wrapper over the installed `gpp`/`msvc`/`win32` scaffolds (requires 0.3.0+; `-Windows`
  keeps the MSVC + Win32 GUI shorthand), pointers name `tj-agents/cpp` and canonical
  identifiers, stale `dotfiles/skill-routes/` snapshots deleted, `claude-global.md` names
  `cpp` plus explicit toolchains, root route profile regenerated (`cpp`). Verified against
  this branch's packages through a temporary plugin registry: `cpp+gpp`, `cpp+msvc`,
  `cpp+msvc+win32`, each `git init` on `main`. The normal checkout's dirty `NORTH_STAR.md`
  edit is untouched.
- [ ] Push the workspace branch and open its PR once v0.3.0 is released and installed.
- [ ] Follow-up for the user: workspace `NORTH_STAR.md` duplicates `cpp:direction` (which
  now defers compiler/debugger/profiler to the toolchain skills). It was not converted to a
  pointer because the normal checkout holds an uncommitted user edit to it.
- [x] Other active consumers: `cpp/gpp/note-cli`, `cpp/windows/icon-dropper`,
  `cpp/windows/wifi-toggle`, `cpp/windows/winwrap` use legacy identifiers served by the
  compatibility packages until 2027-03-31; nothing here breaks them, so they are recorded
  rather than rewritten. Migrate each with `gen_skill_routes.py --toolchain … --api …`
  before the window closes. `sandbox-hwid` is handled by Stage 0.

## Progress

- 2026-09-23 PR #13 merged at `c718b76` after exact-head green checks on `1fe4183`.
  Release preparation validated locally: generator current (220 files / 16 definitions),
  route self-test, 11 hook tests, 52 source tests (1 optional skip), Claude validation of
  the marketplace and nine packages, and isolated Codex installation of all nine.
