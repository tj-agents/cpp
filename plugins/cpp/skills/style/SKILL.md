---
name: style
description: Generic C++ naming, initialization, braces, API documentation, implementation comments, and clang-tidy conventions.
kind: convention
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

- Name types and concepts with the clearest meaningful noun. Let the enclosing namespace
  provide project and subsystem context; do not mechanically append `Record`, `Data`,
  `Model`, `Info`, or a similar category label.
- Add a qualifier only when it distinguishes real coexisting representations or
  responsibilities at a boundary. `IdentityRequest` distinguishes a request from
  `Identity`; `ContextConfig` distinguishes configuration from a context.
- Preserve established names whose qualifiers carry that distinction. For example,
  `winwrap::kernel::driver::Context` needs no repeated driver label, while
  `ObjectContext<T>` names a wrapper rather than the context itself.

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
