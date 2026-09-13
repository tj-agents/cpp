# Library conventions — C++ (Tommy)

How I decide what to depend on. Goal: write plain modern `std::`, and reach for
a backport **only when the standard I'm targeting doesn't have the feature yet.**

## The rule

1. **Default to `std::`, always.** Use the standard library directly. New
   projects target C++23 (g++16), so in practice everything is just `std::`.
2. **Only reach for a backport when my target standard lacks the feature** —
   i.e. on an older-standard project. Never add one to a project whose standard
   already has the type: on a modern compiler the backport is just an alias to
   `std::`, so it's a dependency that buys nothing.
   - **Types** → the `nonstd-lite` family (`nonstd::expected`, etc.): single
     headers that alias to `std::` when present and fall back otherwise, so the
     spelling is identical on every standard. `FetchContent` them in.
   - **Ranges** → `range-v3` (spelled `ranges::`; *not* a drop-in alias to
     `std::ranges`, so only ever on old C++).
3. **Roll my own only as a last resort** — when the std lacks it at the target
   standard, *and* no well-known library covers it, *and* a wrapper meaningfully
   cleans up call sites. Header-only, in a personal `stdx`-style lib.

**Why `std::`-direct, not wrappers-everywhere:** besides avoiding dead
dependencies, reaching for a backport *only when a feature is actually missing*
keeps me aware of **which C++ version introduced what** (`expected` = C++23,
`span` = C++20, `optional`/`variant` = C++17). Wrapping everything in `nonstd::`
would abstract that away and I'd learn less — the "Native since" column below is
part of the point.

(Sole exception to rule 2: a library that must compile across a *range* of
standards at once — there, use `nonstd::` everywhere so one source spans the
matrix. Rare; not my normal single-standard projects.)

## The `nonstd-lite` map (https://github.com/nonstd-lite)

| Need          | Library          | Spelling              | Native since |
|---------------|------------------|-----------------------|--------------|
| expected      | expected-lite    | `nonstd::expected`    | C++23        |
| optional      | optional-lite    | `nonstd::optional`    | C++17        |
| variant       | variant-lite     | `nonstd::variant`     | C++17        |
| string_view   | string-view-lite | `nonstd::string_view` | C++17        |
| span          | span-lite        | `nonstd::span`        | C++20        |
| scope guard   | scope-lite       | `nonstd::scope_exit`  | (not in std) |

## Not covered by the family: ranges

Ranges aren't a `-lite` library (too big to shim that way), but the same
through-line holds — on older C++ you use a backport that mirrors the
future-standard API.

- **Modern C++ (20/23):** use `std::ranges` directly — `std::ranges::sort(v)`,
  `std::ranges::contains`, `std::ranges::find`, member `.contains()`, and views.
- **Older C++ (14/17), full package:** **range-v3** (Eric Niebler) — the prototype
  `std::ranges` was standardized from, so it teaches the real thing. Header-only.
  Namespaces `ranges::` and `ranges::views::`. `FetchContent` it in. Downside:
  heavy — big headers, noticeable compile-time hit.
- **Older C++ (17), slim:** **NanoRange** (Tristan Brindle) — single-header C++17
  implementation of the C++20 ranges API, designed as a lightweight alternative
  to range-v3. Use this when forced onto old C++ and you want `ranges::sort(v)`
  etc. without range-v3's weight. Namespace `nano::` (own impl, not a `std`
  alias — fine, since old C++ has no `std::ranges` to alias to anyway).
  - Pass whole ranges: `ranges::sort(v)` instead of the `v.begin(), v.end()` dance.
  - Lazy, composable views with `|`:
    `v | views::filter(is_even) | views::transform(square)`.
  - Footgun: views are **lazy and non-owning** — nothing is computed until you
    iterate, and the view only refers to the source container. If that container
    dies, the view dangles (same hazard as a dangling reference).
- *Avoid* Boost.Range for new code — superseded by range-v3.
- For just one or two helpers (e.g. a `contains`) on old C++, a tiny personal
  `stdx` helper is fine rather than pulling in all of range-v3.

### The `begin()`/`end()` boilerplate specifically

Already solved by the std on C++20+: `std::ranges::sort(v)`,
`std::ranges::find(v, x)`, `std::ranges::for_each(v, f)` take a whole range — no
`.begin(), .end()`. So **don't hand-roll thin algorithm wrappers, and don't spin
up a personal util lib for this on modern C++** — that's reinventing
`std::ranges`. A personal helper lib is justified only *reactively* (the same
std-less gap recurring across 2–3 projects), never created empty up front.

## FetchContent shape (range-v3)

```cmake
include(FetchContent)
FetchContent_Declare(range-v3
    GIT_REPOSITORY https://github.com/ericniebler/range-v3.git
    GIT_TAG <pin-a-tag>
    GIT_SHALLOW TRUE
    SYSTEM)
FetchContent_MakeAvailable(range-v3)
# target_link_libraries(<target> PRIVATE range-v3::range-v3)
```

## FetchContent shape (expected-lite)

```cmake
include(FetchContent)
FetchContent_Declare(expected-lite
    GIT_REPOSITORY https://github.com/nonstd-lite/expected-lite.git
    GIT_TAG <pin-a-tag>
    GIT_SHALLOW TRUE
    SYSTEM)
FetchContent_MakeAvailable(expected-lite)
# target_link_libraries(<target> PRIVATE nonstd::expected-lite)
```
