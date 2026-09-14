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

Run the repository's focused preset while iterating and report failures with
their test names and output. For the standard scaffold:

```text
cmake --build --preset dev
ctest --preset dev --output-on-failure
```
