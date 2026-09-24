---
name: cpp-testing
description: Generic C++ test-tier, Catch2, CTest, test-target, naming, isolation, and regression-test conventions.
kind: contract
domain: cpp
---

# Testing conventions — C++ (Tommy)

Use Catch2 v3 with CTest for new C++ test suites unless an existing repository
has already standardized on another framework.

## Test the real target

- Put behavior in a library target and link that same target into the app and
  its tests. Never compile a parallel copy of production sources into the test
  executable.
- Register Catch2 cases with `catch_discover_tests`, so CTest owns discovery and
  the build remains usable from editors and CI without a custom runner.
- Mirror production structure under `tests/` and name sources `*_test.cpp`.
- Keep test-only helpers inside the test target; do not add production APIs only
  to make private implementation details observable.

## Compile public headers independently

Give each public header a minimal translation-unit compile check when it has substantial
template or preprocessor implementation. The check catches missing direct includes,
include-order dependencies, and leaked macros. For example:

```cpp
#include <acme/event_kind.hpp>

#if defined(ACME_DETAIL_EVENT)
#error "event_kind.hpp leaked an implementation macro"
#endif

int main() {}
```

Compile this source with only the public target's advertised usage requirements. Do not
include the unsupported `detail/event_kinds.inc` fragment in a consumer-facing header
test: it deliberately requires its setup macro and is not a standalone API. When the
repeatable fragment itself warrants a focused internal test, define the setup macro,
include the fragment, `#undef` the macro, and repeat with a different definition so the
test exercises its intended contract.

## Keep tiers honest

A unit test has no real filesystem, process, network, database, message pump, or
operating-system UI dependency. Test platform-neutral logic at that tier.
Anything that boots or manipulates a real external boundary is an integration
test and must be named and run as such. Platform-specific behavior may need a
separate platform integration target rather than being disguised as a unit test.

## Write useful cases

- Test observable contracts, boundary values, failure results, ownership, and
  state transitions rather than line-by-line implementation.
- Prefer small explicit inputs over shared mutable fixtures.
- A regression test should fail for the demonstrated defect before the fix and
  describe the behavior, not the incident or ticket number.
- Do not weaken or delete an assertion merely to make a red run pass; diagnose
  whether the implementation, expectation, or test tier is wrong.

For composed behavior, test through the host's public operation rather than only
instantiating the provider templates. Cases should prove:

- each non-overlapping event reaches its intended behavior;
- an unhandled event falls through to the next provider;
- overlapping conditions follow the documented first-match rule;
- reordering providers changes behavior only where the public contract permits it;
- shared or provider-owned state moves through the intended transitions; and
- callbacks, references, views, and resource-owning bases do not outlive their owners.

A compile-only assertion is useful for composition constraints, but it cannot prove which
handler ran, whether a later handler was shadowed, or whether coupled state and lifetimes
remain valid.

Run the repository's focused preset while iterating and report failures with
their test names and output. For the standard scaffold:

```text
cmake --build --preset dev
ctest --preset dev --output-on-failure
```
