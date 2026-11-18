---
name: errors
description: C++ error policy, typed failure vocabulary and fallible result contracts. Use when choosing or consuming an error result, placing component errors, or checking noexcept and language-baseline requirements.
kind: standard
domain: cpp
profile: core
applicability: C++ projects
requires: cpp
provenance: house
---

# Error contracts in C++

Owns C++ error policy, typed failure vocabulary and fallible result contracts.

## Result and failure contracts

Use the repository's established error policy. In C++23, `std::expected<T, E>` can express
a result or a meaningful error; `std::expected<void, E>` suits fallible validation.
Prefer an enum for a closed set of failures, or a small structured error when callers
need context. Check the result before accessing the value. Do not flatten recoverable
errors into `bool`, strings, or assertions when callers need to distinguish them.
Keep diagnostics/logging at the boundary rather than repeating them at each return.

`std::expected` does not make the operation non-throwing by itself. Allocations and
called code still follow their own contracts. Mark `noexcept` only when justified.
Honor a consumer's actual language/library baseline; do not impose C++23 library types
on a C++17 ABI or restricted environment.

```text
C++23 result: std::expected<Identity, IdentityError> from Identity::decode.
Success: inspect the result before accessing Identity.
Recoverable failures: IdentityError::length, IdentityError::profile or IdentityError::text.
Diagnostics: reported at the boundary.
A C++17 ABI or restricted environment keeps its established supported error contract.
```

## Error vocabulary ownership

- The type's API header declares its errors beside the type. A dedicated error header is
  appropriate when that same component has enough shared vocabulary to justify one;
  a generic `validation.hpp` or application-wide `errors.hpp` should not own unrelated rules.

## Consumer baselines

Respect each consumer's actual language and library baseline. A public header exposing
`std::expected` requires C++23, and its build target must propagate that requirement.
Do not let grouping force unsupported dependencies onto another runtime.

`cpp:domain-design` owns the representations, validation and decoding operations using these contracts.
