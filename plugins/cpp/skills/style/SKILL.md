---
name: style
description: Generic C++ naming, initialization, braces, API documentation, implementation comments, and clang-tidy conventions.
kind: contract
domain: cpp
---

# Code conventions — C++ (Tommy)

Idiomatic modern C++, not Google style.

Use `cpp:domain-design` when choosing records, invariants, factories, operations, or
stateful boundaries. This skill owns their spelling and formatting.

## Naming

- **Private member variables:** trailing underscore — `name_`, not `m_name`
- **Constants:** no prefix — `constexpr auto notes_filename = "notes.txt"`, not `k_notes_filename`
- **Everything else:** snake_case for variables/functions, PascalCase for types/classes

### Semantic type names

- Name domain and value types with the clearest noun for the concept they represent.
  Let the enclosing namespace provide project and subsystem context.
- Add a role suffix when it distinguishes real coexisting representations or
  responsibilities at a boundary.

### Behavior-provider names

Name a mixin for the behavior it adds, not for the fact that it uses inheritance. Use an
`-able` name selectively when it expresses a real capability, such as `FileDroppable`.
Use natural role names for observed events and protocol responsibilities, such as
`ConnectionObserver` and `CommandRouter`; do not impose one suffix on every provider.

## Namespaces

- Put reusable and shared code in a stable top-level namespace owned by the project or
  library. Derive its name from that owner and write namespace components in snake_case.
- Use that project/library namespace by default. Add a nested namespace when it names
  a cohesive subsystem, shared contract, or distinct set of responsibilities. A known
  boundary can be explicit from the outset; do not wait for a collision or another consumer.
- Do not automatically mirror folders or put every feature or domain noun in its own
  namespace. File ownership and build-target boundaries do not require another namespace.
- Preserve meaningful concept names such as `Identity` and `IdentityRequest`. Namespace
  context can remove redundant project prefixes, but does not justify replacing a clear
  domain noun with a generic name merely to shorten its qualification.
- Introduce a `domain` namespace when the codebase has an explicit domain layer whose types
  must be distinguished from protocol, persistence, or presentation representations.
- Qualify names at public and cross-namespace boundaries. In implementation files, use
  narrow using-declarations or namespace aliases when they improve local readability.

## Initialization

- Always use `{}` over `()` for construction — avoids most vexing parse and prevents narrowing conversions
- Exception: `std::vector<int> v(10)` (10 elements) vs `v{10}` (1 element with value 10) — be explicit

## Integer widths and aliases

- Use `std::uint16_t`, `std::uint32_t`, and the other exact-width types from `<cstdint>`
  when an owned binary format, wire contract, register, or ABI field requires that width.
  Let the field or variable name express its role.
- Use a `using` alias when it makes a genuine generic or platform-independent relationship
  clearer. Use a distinct wrapper type when incompatible values require compiler-enforced
  separation; aliases remain interchangeable with their underlying type.
- For a shared binary ABI, pair exact-width fields with assertions for total sizes and
  significant offsets so padding and ordering are checked. Keep these when adding static
  validation or adopting domain modelling; neither establishes a binary layout contract.

## Constants — named, at their contextual boundary

Every magic value (sentinel, id base, size, flag combo) gets a **named
`constexpr`** — no bare literals at call sites. Scope it to the **narrowest
boundary that covers all its uses** ("contextual boundary"):

- used by one function → function-local `constexpr`
- shared across one class's members → `static constexpr` member on that class
- shared across a header/component → namespace-scope `constexpr` in that header
- file-local in a `.cpp` → anonymous namespace

Example: `query_count` (the `0xFFFFFFFF` count-query sentinel of
`DragQueryFileW`) lives *inside* `Drop::count()` — its only user — not on the
class or the file. Widen a constant's scope only when a second user appears
(the same reactive rule as code extraction, winwrap `CODE_CONVENTIONS.md §3`).

## Braces

- **Omit braces for a single-statement body** — `if`, `else`, and loops; the body
  goes on its own indented line, no braces (clang-format enforces this via
  `AllowShortIfStatementsOnASingleLine: Never` and `AllowShortLoopsOnASingleLine: false`).
  Best for guard clauses.
- **Keep braces** when the body is multiple statements, wraps across lines, or is
  itself a control structure (a nested `if`/loop) — clarity wins there.
- **`if`/`else` stay symmetric:** if either branch needs braces, both get them.

## Documentation comments (Doxygen)

- **Style:** triple-slash `///` with `@`-prefixed commands (`@param`, `@return`,
  `@tparam`, `@throws`, `@note`). Canonical in modern C++ (LLVM/Clang use it),
  matches C# XML-doc, and avoids the `/** … */` block's ` * ` gutter noise.
- **Lead with a one-line brief** — the first line is the summary; no explicit
  `@brief` needed.
- **Where:** the **public API** in headers — types, public/protected member
  functions, free functions. This is API documentation, distinct from the
  "comments are rare" rule below, which still governs *implementation* comments
  inside function bodies (those stay terse `//`, why-not-what).
- **Don't over-document:** omit `@param`/`@return` when the name already says it
  (a trivial getter gets a one-line brief, nothing more). Spend words on the
  non-obvious: preconditions, ownership, error/throw behaviour, units, lifetimes.
- **Struct / data members:** the Doxygen idiom for fields is a per-member comment
  — a trailing `///<` after the declaration (that syntax exists for exactly this).
  Use it for structs whose fields carry non-obvious contracts (ownership, units,
  sentinels, preconditions). For a small struct whose field names already say
  everything, a single `///` brief above the struct with bare fields is fine.
  **Mixing within a struct is fine:** put a `///<` on the fields that carry a
  non-obvious contract and leave genuinely self-evident ones (`width`, `height`, …)
  bare — never add a `///<` that only restates the field's name. Readability decides.
- Don't Doxygen private/impl details — a plain `//` where genuinely needed.

## Misc

- Anonymous `namespace { }` for file-local helpers and constants (instead of `static`)

## Contain preprocessor macros

A macro cannot live in a C++ namespace. Give every library macro a library-specific
prefix, define an implementation macro only around the expansion that needs it, and
`#undef` it before the public header finishes. A namespace qualification does not prevent
collisions or leakage.

Use a deliberately repeatable internal include fragment only when the same declaration
list must be expanded in more than one form. For example, an unsupported
`acme/detail/event_kinds.inc` fragment may contain:

```cpp
#ifndef ACME_DETAIL_EVENT
#error "Define ACME_DETAIL_EVENT before including this internal fragment"
#endif

ACME_DETAIL_EVENT(file_drop)
ACME_DETAIL_EVENT(command)
```

A public header that genuinely needs both the enum and its stable display names contains
each expansion locally:

```cpp
#include <string_view>

namespace acme {

enum class EventKind {
#define ACME_DETAIL_EVENT(name) name,
#include <acme/detail/event_kinds.inc>
#undef ACME_DETAIL_EVENT
};

[[nodiscard]] constexpr std::string_view event_name(EventKind event) noexcept {
    switch (event) {
#define ACME_DETAIL_EVENT(name) case EventKind::name: return #name;
#include <acme/detail/event_kinds.inc>
#undef ACME_DETAIL_EVENT
    }
    return {};
}

} // namespace acme
```

Each include gets its own adjacent `#define`/`#undef` pair. The `.inc` file deliberately
has no `#pragma once` or include guard: repeatability is its contract. Keep it under
`detail/`, require the setup macro with `#error`, and never expose that macro as part of
the supported API. Prefer an ordinary `constexpr` table, template, or function when
repeated preprocessing is unnecessary. `cpp:structure` owns the unsupported compatibility
meaning of `detail/`; `cpp:testing` owns the independent public-header leakage check.

## Lint (clang-tidy)

- **The compiler is the source of truth.** When a clang-tidy check conflicts with a
  compiler warning — e.g. `readability-named-parameter` wants a parameter named that
  MSVC `/W4` then flags as `C4100` (unreferenced formal parameter) — the compiler
  wins: suppress the tidy check.
- **Triage each warning; don't blanket-ignore.** If a check is *wrong or inapplicable*
  for the pattern, disable it in `.clang-tidy` with a comment saying why. If it's
  *legitimate*, fix the code. (E.g. match an SDK-declared parameter name such as
  `wWinMain`'s `nShowCmd` → fix; a callback/hook method flagged "could be static" →
  suppress: hooks are instance methods by contract.)
