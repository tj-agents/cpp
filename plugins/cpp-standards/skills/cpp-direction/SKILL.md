---
name: cpp-direction
description: Tommy's C++ learning destination and tooling skill tree used when choosing or sequencing learning work.
kind: knowledge
domain: cpp
---

# North Star — where I'm headed with C++ (Tommy)

The destination these projects are driving toward. `KNOWLEDGE.md` tracks where
I am *now*; this file tracks where I'm going and *how* I want to get there.

## The goal

Become a **versatile, "cracked" C++ developer** — not just someone who can make
the language work, but someone who's comfortable across the whole ecosystem that
surrounds C++ and could be dropped into any codebase and be productive.

I came to C++ through LeetCode (single-file, compile-and-run), so the gap I'm
closing is everything *around* the language: build systems, tooling, libraries,
project structure. That's the real skill, and it's what these projects exist to
build.

## The skill tree (the 8 areas I'm specializing in)

Framing borrowed from CJ's "C++ wretch" video. My current pick for each — these
are the tools I'm learning with, not final opinions:

| # | Area | My pick | Status |
|---|------|---------|--------|
| 1 | Build system / generator | **CMake** (+ presets) | learning now |
| 2 | Debugger | **Selected by platform layer** | see Windows/GCC layer |
| 3 | IDE / terminal | **VS Code** + **Neovim**; getting comfy in the terminal | learning now |
| 4 | Testing framework | **Catch2** | seen it (keystore tests) |
| 5 | Compiler | **Selected by platform layer** | see Windows/GCC layer |
| 6 | Linting / formatting | **clang-tidy** + **clang-format** | configured, not deeply understood |
| 7 | Profiler | **Selected by platform layer** | see Windows/GCC layer |
| 8 | Version control | **git** | basics |

When I level up an area, note it here.

## How I want to get there (the rule)

**These projects are for learning, not for output.** The point is that *I*
understand the code and can write it myself — not that the project gets finished
fast.

So, when working with me:

- **Don't just write the code for me.** Explain the idea, show me the shape, and
  let me write as much as I can myself. If you do write code, walk through *why*
  it's written that way so I could reproduce it.
- **Teach the tooling, not just the language.** When CMake, a platform-selected
  compiler/debugger/profiler, clang-tidy, or git comes up, treat it as something
  to *learn*, not boilerplate to skip past —
  they're explicitly on the skill tree above.
- **Prefer understanding over speed.** A slower path where I get it beats a fast
  path where I don't.
- **Check that it landed.** It's fine to ask me to explain something back, or to
  try writing the next piece myself before you show yours.

See also: `cpp-standards:cpp-knowledge` for the current level and
`cpp-standards:cpp-learning` for how to work with me.
