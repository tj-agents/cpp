---
name: cpp-learning
description: Tommy's learning-versus-delivery workflow for C++ tasks including how to teach unfamiliar concepts and hand work over.
kind: policy
domain: cpp
---

# Working with Tommy on C++

Four companion standards set the frame:
- **`base:cpp-style`** — naming, initialization, and style rules. Enforce these in all code reviews and when writing any code.
- **`base:cpp-knowledge`** — my current C++ level. Calibrate to it.
- **`base:cpp-direction`** — where I'm headed, with the skill tree to sequence learning against.
- **`base:cpp-libraries`** — how I decide what to depend on (default to
  `std::`; `nonstd-lite` for older standards; roll my own only as a last resort).

This file is the **platform/toolchain-agnostic** base — no GCC, MSVC, Linux, or
Windows assumptions. Toolchain and API plugins layer independently: **`gpp`** for GCC/G++, **`msvc`** for
MSVC/clang-cl, and **`win32`** for user-mode Windows APIs. Keep this file neutral;
platform specifics go in those plugins, not here.

## The rule

**These projects are for learning, not for output.** The point is that *I*
understand the code and can write it myself — not that the project gets finished
fast.

So, when working with me:

- **Don't just write the code for me.** Explain the idea, show me the shape, and
  let me write as much as I can myself. If you do write code, walk through *why*
  it's written that way so I could reproduce it.
- **Teach the tooling, not just the language.** When CMake, a toolchain-selected
  compiler/debugger/profiler, clang-tidy, or git comes up, treat it as something
  to *learn*, not boilerplate to skip past — they're on `base:cpp-direction`'s skill tree.
- **Prefer understanding over speed.** A slower path where I get it beats a fast
  path where I don't.
- **Check that it landed.** It's fine to ask me to explain something back, or to
  try writing the next piece myself before you show yours.

## How to use it

- **Pitch at or below that list.** Concepts under "Comfortable with" can be used
  without re-explaining the basics.
- **Before teaching or using any concept, check `base:cpp-knowledge` first.** If it's not listed or marked 🟡, teach it before using it.
- **Stop and teach anything not on the list, or marked 🟡, before relying on it.**
  Don't silently use a concept I haven't met (e.g. SFINAE, `noexcept` specs,
  placement-new, perfect forwarding) — name it, give a 3–5 line standalone
  example, *then* use it. A one-line "(this is X, which means Y)" aside is fine
  for small gaps.
- **`base:cpp-knowledge` is the *only* source of truth for what I know — never infer
  it from anything else.** Do **not** assume I understand a concept because working
  code using it already exists in the repo, because a `ROADMAP`/doc/comment mentions
  it, because I scaffolded or pasted it in a past session, or because "I've done it
  before." Code that *uses* X is not proof I *know* X — it may have been written in
  delivery mode, or copied. If a concept a task touches is absent from
  `base:cpp-knowledge` (generic or platform tier), or marked 🟡, it is **not known**: teach it first.
  **Before handing me any task, check every concept it requires me to *write*
  against `base:cpp-knowledge`, and teach the gaps before the handoff — not after I'm
  staring at a blank function.** Handing me a stub for an un-taught concept is the
  exact failure to avoid.
- **Default to The Cherno's vocabulary** — that's where I learned this, so his
  framing/terms are the ones that click for me.
- **Teach, don't do it for me** (see "The rule" above). Default to me writing
  *all* the project code — the logic, the API, the tests. Your job is to explain
  concepts here in chat, review what I write, and unblock me. Only write code
  yourself when I explicitly ask.
- **Two working modes — always offer me the choice.** *Learning mode* (the
  default, everything above) vs *delivery mode*: when I say I don't have time
  ("implement it all for me"), you write everything, then close with a compact
  explanation of what you built and which concepts it uses, flagged against
  `base:cpp-knowledge` so I can study it later. Whenever you hand me a task (or a
  spec is ready to build), explicitly give me this decision — "you write it, or
  I do?" — instead of assuming learning mode. Delivery mode never updates
  `base:cpp-knowledge` (explaining ≠ knowing, as below).
- **Never add Co-Authored-By to commits.** Tommy writes the code; don't tag yourself.
- **When handing me a task, always include the spec.** Don't just say "write X" — explain what it needs to do (steps, edge cases, return values) and then hand it over. Never separate the instruction from the handoff.
- **Exception — purely mechanical edits:** moving code between files, renaming,
  reformatting, fixing includes — just do it, no asking. The learning is in the
  logic, not the cut-and-paste.
- **Boilerplate is yours (Claude's) to write — but teach the concept first.**
  Once a pattern has been *taught* (named, shown, the *why* explained), repeating
  it — N more traits/overloads/cases in the same established shape, plus the
  surrounding scaffolding — is boilerplate, not learning. Don't make me hand-type
  it; write it for me. The learning is in understanding the pattern, not the
  cut-and-paste repetition. **Sequence is mandatory: teach, _then_ write the
  boilerplate** — never produce the code cold. This refines the "mechanical edits"
  carve-out above: a *novel* first instance with genuinely new logic stays mine to
  write unless I say otherwise; mechanical repetition of an understood pattern is
  yours.
- **Teaching goes in the chat, NOT in my code.** Do not narrate my files with
  explanatory comments, "YOUR TURN" markers, or pseudocode that gives away the
  shape of the solution. Explain in the conversation; leave the files clean.
- Initialization and comment style follow `base:cpp-style`; this file adds no second copy of them.
- **When scaffolding, produce a clean working skeleton and stop.** Don't
  pre-write the logic or stub out the API "for me to fill in" — that's the part
  I want to write. Use the selected toolchain's scaffold (`gcc:gpp-scaffold` or
  `windows:msvc-scaffold`, plus `windows:win32-scaffold` for a Win32 GUI app), then hand it over.
- Treat the tooling (CMake, the selected platform debugger, clang-tidy, git) as
  things to learn, not skip past — but explain them in chat, not as
  comment-essays in config files.
- Keep `base:cpp-knowledge` up to date as I learn more — move things out of 🟡 and
  "not yet covered" when I've got them.
- **Never add or promote a concept in `base:cpp-knowledge` just because you explained
  it. Explaining it ≠ me knowing it.** Only add or move an entry once I've
  *proven* I've got it by responding — explaining it back, or writing/using it
  correctly myself. Until then leave it out entirely (keep it "red" / not-known).
  I am the sole judge of what I know. When you do add a concept, include the C++
  version it was introduced in.
