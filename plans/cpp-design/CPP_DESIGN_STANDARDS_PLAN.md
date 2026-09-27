# C++ design standards and canonical skill names

## Objective

Publish one reusable, idiomatic C++ design standard derived from established DDD vocabulary,
the C++ Core Guidelines, and explicit state/logic separation, then apply its decisions to the
Sandbox HWID lab as a foundation for a growing, multi-feature system. Current code size is
not a reason to flatten ownership or postpone useful module boundaries. Separate scalable
architecture from inventing domain invariants that the present wire records do not have.

## Authorization

Tommy authorized completing the research and reusable agent guidance, correcting redundant
skill names, and applying the resulting design to the current lab. Driver installation,
loading, signing-policy changes, VM operations, and unrelated WinWrap implementation remain
outside this work.

Completed steering (2026-09-23): Tommy authorized updating existing cpp-agents PR #13 and the
Sandbox HWID application to use type-owned static request validation and the identity
feature namespace. Retain and explain the ABI assertions. This turn updates the review
candidate and sandbox; it does not claim or require a merge, publish a release, or expand
driver/runtime scope. The earlier Claude handoff produced the commits recorded below.

Completed namespace steering (2026-09-23): apply a project/library namespace by default and add nested
namespaces for meaningful subsystem or contract boundaries. Keep `Identity` and
`IdentityRequest`; use `sandbox_hwid::protocol` for the shared client/driver wire contract.
Keep namespace depth independent of folders and architectural scale. A useful library
boundary does not require a second consumer. Update the existing guidance and sandbox PRs;
no wider product-tree reorganization was selected. Keep process notes brief.

Completed response-validation steering (2026-09-23): put response rules and their typed errors with `Identity`,
leaving byte-length checking, copying and delegation in the client decoder. Apply this
ownership rule to the reusable standards as well as the sandbox and update the existing PRs.

Latest steering (2026-09-23): Tommy accepted the completed design and said "lets go".
Implement the member decoder, device component and corresponding reusable standards,
validate the actual projects, and update the existing review candidates. The prior
discussion-only pause is lifted. Preserve unrelated work and the separate restrictions
on merging, driver execution, signing, installation and VM operations.

## Settled decisions

- Canonical skill identifiers use the plugin as the namespace and a non-redundant capability
  name: `cpp:style`, `cpp:build`, `gpp:toolchain`, `msvc:toolchain`, and `win32:style`.
- Existing redundant identifiers remain only as time-bounded compatibility aliases where the
  published compatibility window requires them.
- The reusable design capability is `cpp:domain-design`.
- DDD supplies modelling vocabulary and boundaries; it does not require inheritance-heavy OOP,
  a `domain` namespace/folder, or a class for every data type.
- Use a `struct` for passive data whose members may vary independently. Use a `class` when a
  real invariant requires controlled construction or representation.
- A fallible factory such as `create` establishes a valid value. Member functions represent
  operations on an encapsulated value. Prefer a static member such as `IdentityRequest::validate`
  for a stateless check owned by that one type when grouping makes the API clearer. Associated
  free functions remain appropriate for independent algorithms and boundary adapters. This
  grouping preference is a house decision, not a requirement of C.4/C.5 or DDD.
- Types own their validation rules and typed errors. Representation adapters check framing,
  copy or convert input, then delegate without duplicating those rules. An intrinsic
  representation can be decoded by its own type. Keep user-mode C++23 includes/methods
  outside the kernel view; expose the actual language requirement to each consumer.
- Immutable transformations use a domain-specific verb. `with_x` is available when it truly
  means "copy this value with one replacement" but is not a mandated C++ naming pattern.
- C++ value semantics do not require an immutable API. Prefer immutable domain values when
  that simplifies reasoning; preserve efficient local mutation and invariant-preserving
  member operations where appropriate. A fallible factory is useful for expected invalid
  input, not a mandatory substitute for every constructor.
- Keep mutable state and external I/O in coarse boundary components; keep core transformations
  explicit and independently testable.
- Sandbox HWID currently has passive wire records, not a behaviour-bearing domain model.
  Their struct representation, validation semantics and ABI checks remain appropriate within
  a scalable architecture. Preserve the names `Identity` and `IdentityRequest`. The published
  contract namespace is `sandbox_hwid::protocol`; it names the shared wire boundary
  without imposing a namespace on every feature or folder. Ordinary static functions do not alter object layout.

## Work

### 1. Reusable cpp-agents source

- [x] Perform an independent research pass before authoring: use primary or authoritative
      sources for DDD vocabulary, C++ Core Guidelines, modern C++ value-oriented design,
      state/effect separation, naming, and representative production-library practice.
      Distinguish sourced conventions from deliberate house decisions, challenge the settled
      draft where evidence disagrees, and retain concise source rationale for the final report.
- [x] Rename canonical authored skill capabilities to remove duplicated scope words.
- [x] Preserve the documented compatibility packages and their old identifiers through the
      existing 2027-03-31 window.
- [x] Add `cpp:domain-design` with generic examples covering passive records, invariant-bearing
      values, fallible factories, immutable transformations, associated free functions,
      stateful adapters, entities/value objects, typed errors, and namespace ownership.
- [x] Update routes, manifests, source/package mappings, documentation, hooks, tests, and
      generated outputs from their canonical owners.
- [x] Validate generator freshness, route self-tests, hooks, package contracts, host validators,
      and scaffold acceptance checks required by `AGENTS.md`.

### 2. Sandbox HWID application

- [x] Update the lab to the canonical installed skill identifiers after the reusable package is
      available.
- [x] Apply role-based protocol naming: `IdentityRequest`, `IdentityRequestError`,
      `IdentityError`, and `query_identity` (the original free validator is superseded below).
- [x] Keep `Identity` as a passive ABI record and record why a separate domain model is
      not currently justified.
- [x] Preserve the client/kernel ABI and all explicit host-versus-VM safety boundaries.
- [x] Run the authorized host build, tests, formatting, static analysis, and real WDK build as
      applicable; do not install or load the driver.

### 3. Function ownership and feature namespace correction (2026-09-23)

- [x] Correct canonical domain-design/style guidance, regenerate packages, and validate.
- [x] Move sandbox request validation to `IdentityRequest::validate` and use
      `sandbox_hwid::identity` consistently in namespaces, headers, consumers and current docs.
- [x] Preserve ABI assertions and validate standard-layout, aggregate and trivial-copy traits;
      rerun the real client/tests and C++17 WDK build/analysis.
- [x] Commit the bounded corrections, update existing cpp-agents PR #13, and publish a
      reviewable sandbox companion candidate without staging unrelated work.

### 4. Namespace and scalable module correction (2026-09-23)

- [x] Preserve `Identity` and `IdentityRequest`; remove the automatic feature-namespace rule.
- [x] Use `sandbox_hwid::protocol` for the shared wire contract and its decoder; update
      public include paths, consumers, WDK project references and current conventions.
- [x] Clarify that namespace hierarchy need not mirror folders, and that one consumer is
      sufficient for a useful library API, dependency boundary or independent testing.
- [x] Regenerate packages, validate the required source/host checks and rebuild the sandbox.

The existing client, driver and shared roots retain their ownership. The shared ABI remains
C++17 without user-mode dependencies; the client decoder remains C++23. Type-owned static
validation and all size/offset checks stay in place. No new domain model or operation names
are needed for this correction.

### 5. Response validation ownership (2026-09-23)

- [x] Document type-owned rules/errors and representation-adapter delegation in the canonical
      design skill, then regenerate its packages.
- [x] Move response field checks and `IdentityError` into the shared identity header; make
      the C++23 decoder check length, copy, delegate and propagate the same error categories.
- [x] Complete host validation, update current documentation and refresh the lab's guidance.
- [x] Commit and update source PR #13 and sandbox draft PR #1, preserving unrelated work.

### 6. Member decoder and device component (2026-09-23)

- [x] Complete and validate the final design with the user.
- [x] Implement `Identity::decode`, private text checking and the device component.
- [x] Update actual CMake consumption requirements, public API tests and current docs.
- [x] Update authored domain-design/structure guidance and regenerate compatibility packages.
- [x] Pass the actual client/tests, WDK Debug/Release analysis, formatting and clang-tidy checks.
- [x] Pass the source/host checks, refresh installed cpp guidance and preserve unrelated work.
- [x] Commit and update both existing PRs; verify remote heads and source CI/provenance.

### 7. General behavior ownership standard (2026-09-27)

- [x] State the general preference that a meaningful concept owns its cohesive data and
      behavior, including construction, decoding, validation, queries, transformations,
      and permitted state changes where relevant.
- [x] Preserve associated free functions for isolated behavior, cross-type algorithms and
      operations without a natural single owner; do not prescribe empty service classes or
      a domain layer.
- [x] Regenerate the affected canonical and compatibility packages, record the required
      patch versions, run the required source and host validations, and deliver the
      verified cpp-agents change through a personal GitHub PR.

## Acceptance criteria

- Canonical examples read as ordinary modern C++, not translated C# or a prescribed OO style.
- No canonical identifier repeats its namespace (`cpp:cpp-*`, `gpp:gpp-*`, and equivalent
  forms are absent outside compatibility fixtures/documentation).
- Compatibility consumers continue resolving their published old identifiers.
- Generated packages and routes are reproducible and all required repository checks pass.
- The lab builds and its host tests pass with unchanged wire layout and no driver execution.
- The final explanation includes generic examples plus the concrete Sandbox HWID mapping.

## Final design: explicit state and type-owned operations

Design completed on 2026-09-23 at Tommy's request. Keep the selected public include prefix
`sandbox_hwid/` and the `protocol/` contract boundary. This section supersedes the earlier
free-decoder and temporary `IdentityResult` proposals. Tommy subsequently authorized
implementation; the header/decoder/device code, build boundaries and reusable guidance
below are now applied and locally validated. Delivery status is recorded in Progress.

### Ownership and API

| Owner | Public API | Internal work |
|---|---|---|
| `protocol::IdentityRequest` | Static `validate(request)` returning `IdentityRequestError` | Kernel-compatible field checks on an already copied request |
| `protocol::Identity` | Static user-mode `decode(bytes, requested_profile)` returning `std::expected<Identity, IdentityError>` | Length check, local copy, metadata checks, private static `valid_text` |
| `sandbox_hwid::device` | `find()`, `open(path)`, `query_identity(connection, profile)` | Discovery, handle acquisition and synchronous device I/O |
| Executable | CLI arguments, output and probe/stress command scenarios | Calls the device component; formats diagnostics at the outer boundary |

`Identity::decode` is the only public response-validation entry point. Its body owns the
metadata rules directly and calls its private text helper. Remove the separate public
`Identity::validate`; a second metadata-validation method is unnecessary when there is
only one caller. The helper is a named private static member, defined in `identity.cpp`.
It does not need `constexpr`: this decoder handles received bytes at runtime. Keep
`IdentityRequest::validate` constexpr and available to the driver.

All seven Identity data members and all four request data members remain public in their
original order and representation. A private function does not make the data private, add
state, or remove aggregate/standard-layout/trivially-copyable properties. Keep every ABI
size/offset assertion and trait checks. These are editable wire records, not encapsulated
DDD Value Objects; successful decoding validates this copy at this boundary.

Keep `IdentityRequestError` and `IdentityError` beside their types in `identity.hpp`.
`IdentityError` contains failures only: `std::expected` carries success, so remove the
now-unused `IdentityError::none`. Preserve the numeric values of the six existing failure
categories (length through text, 0 through 5). Request validation still uses its existing
`IdentityRequestError::none` success value in the kernel-compatible API.

Keep the existing version, profile, flag and text-capacity constants public in `protocol`:
producers, consumers and contract tests use them. Keep the printable-ASCII bounds private
to `valid_text`. Do not create an anonymous namespace in the public header.

### Implemented identity header

`shared/include/sandbox_hwid/protocol/identity.hpp`:

```cpp
#pragma once

#include <basetsd.h>
#include <stddef.h>

#if !defined(_KERNEL_MODE)
#include <cstddef>
#include <expected>
#include <span>
#endif

namespace sandbox_hwid::protocol {

inline constexpr UINT32 protocol_version{1};
inline constexpr UINT32 baseline_profile{0};
inline constexpr UINT32 alternate_profile{1};
inline constexpr UINT32 synthetic_flag{1};
inline constexpr size_t text_capacity{48};

/// Request failures independent of NTSTATUS and the user-mode runtime.
enum class IdentityRequestError { none, size, version, profile, reserved };

/// Version 1 request. Reserved must be zero; profile selects a caller-local view.
struct IdentityRequest {
    UINT32 size;
    UINT32 version;
    UINT32 profile;
    UINT32 reserved;

    /// Requires an already copied, complete IdentityRequest object.
    [[nodiscard]] static constexpr IdentityRequestError validate(
        const IdentityRequest& request) noexcept {
        if (request.size != sizeof(IdentityRequest))
            return IdentityRequestError::size;
        if (request.version != protocol_version)
            return IdentityRequestError::version;
        if (request.profile != baseline_profile && request.profile != alternate_profile)
            return IdentityRequestError::profile;
        if (request.reserved != 0)
            return IdentityRequestError::reserved;
        return IdentityRequestError::none;
    }
};

/// Decode failures; category values are retained for client diagnostics.
enum class IdentityError { length, size, version, profile, flags, text };

/// Fixed Windows ABI. Text is nonempty printable ASCII, NUL-terminated and zero-padded.
struct Identity {
    UINT32 size;
    UINT32 version;
    UINT32 profile;
    UINT32 flags;
    char serial[text_capacity];
    char model[text_capacity];
    char source[text_capacity];

#if !defined(_KERNEL_MODE)
    /// Copies and validates a complete version 1 wire response.
    [[nodiscard]] static std::expected<Identity, IdentityError> decode(
        std::span<const std::byte> bytes, UINT32 requested_profile) noexcept;

private:
    static bool valid_text(std::span<const char, text_capacity> text) noexcept;
#endif
};

static_assert(sizeof(IdentityRequest) == 16);
static_assert(offsetof(IdentityRequest, size) == 0);
static_assert(offsetof(IdentityRequest, version) == 4);
static_assert(offsetof(IdentityRequest, profile) == 8);
static_assert(offsetof(IdentityRequest, reserved) == 12);
static_assert(sizeof(Identity) == 160);
static_assert(offsetof(Identity, size) == 0);
static_assert(offsetof(Identity, version) == 4);
static_assert(offsetof(Identity, profile) == 8);
static_assert(offsetof(Identity, flags) == 12);
static_assert(offsetof(Identity, serial) == 16);
static_assert(offsetof(Identity, model) == 64);
static_assert(offsetof(Identity, source) == 112);

}  // namespace sandbox_hwid::protocol
```

The `_KERNEL_MODE` guard surrounds both the C++23 includes and the user-mode methods.
Only the user-mode API varies; no data field or layout assertion is conditional.
The client and driver are separate programs. Every translation unit linked into one
program must use the same target configuration and therefore the same class definition.
Do not select this API using include order or per-file feature macros. User-mode consumers
of this header require C++23; the existing WDK C++17 target remains independently configured.
This is the sandbox's explicit platform adaptation, not a generic recommendation to
conditionalize domain APIs or to add user-mode dependencies to kernel builds.

### Implemented identity implementation

`client/src/identity.cpp`:

```cpp
#include "sandbox_hwid/protocol/identity.hpp"

#include <cstring>

namespace sandbox_hwid::protocol {

std::expected<Identity, IdentityError> Identity::decode(std::span<const std::byte> bytes,
                                                        UINT32 requested_profile) noexcept {
    if (bytes.size() != sizeof(Identity))
        return std::unexpected{IdentityError::length};

    Identity record{};
    std::memcpy(&record, bytes.data(), sizeof(record));

    if (record.size != sizeof(Identity))
        return std::unexpected{IdentityError::size};
    if (record.version != protocol_version)
        return std::unexpected{IdentityError::version};
    if (record.profile != requested_profile ||
        (record.profile != baseline_profile && record.profile != alternate_profile))
        return std::unexpected{IdentityError::profile};
    if (record.flags != synthetic_flag)
        return std::unexpected{IdentityError::flags};
    if (!valid_text(record.serial) || !valid_text(record.model) || !valid_text(record.source))
        return std::unexpected{IdentityError::text};

    return record;
}

bool Identity::valid_text(std::span<const char, text_capacity> text) noexcept {
    constexpr unsigned char first_printable{0x20};
    constexpr unsigned char last_printable{0x7e};
    if (text.front() == '\0')
        return false;

    bool terminated{false};
    for (const char value : text) {
        if (value == '\0') {
            terminated = true;
        } else {
            const auto character{static_cast<unsigned char>(value)};
            if (terminated || character < first_printable || character > last_printable)
                return false;
        }
    }
    return terminated;
}

}  // namespace sandbox_hwid::protocol
```

The decoder checks exact length before copying into an aligned local object; it never
casts untrusted bytes to an Identity pointer. It checks the declared size, version,
requested/recognized profile, exact synthetic flag, and all three text fields once.
`valid_text` accepts nonempty printable ASCII followed by a terminator and zero padding;
its final `return terminated` is necessary to reject a full field without a terminator.
`noexcept` is justified here by the bounded checks, trivial value/error copies and absence
of allocation or external I/O. The returned Identity owns its bytes.

### Device API and error policy

`client/include/sandbox_hwid/device.hpp`:

```cpp
#pragma once

#include <windows.h>

#include <wil/resource.h>

#include <string>

#include "sandbox_hwid/protocol/identity.hpp"

namespace sandbox_hwid::device {

/// Finds the sole present synthetic device interface; throws on failure.
[[nodiscard]] std::wstring find();

/// Opens the given interface; the returned handle owns its lifetime.
[[nodiscard]] wil::unique_hfile open(const std::wstring& path);

/// Borrows the handle for one synchronous request; throws on transport or protocol failure.
[[nodiscard]] protocol::Identity query_identity(HANDLE connection, UINT32 profile);

}  // namespace sandbox_hwid::device
```

Move the existing discovery/open/query implementations from `main.cpp` into `device.cpp`.
Use the namespace boundary for context: `find_device` becomes `device::find`, and
`open_device` becomes `device::open`. Preserve the meaningful verb `query_identity`.
The handle returned by `open` owns the resource through WIL; `query_identity` borrows a
valid handle for its synchronous call and does not close it. The query builds the request,
performs DeviceIoControl, checks the returned count against its buffer before taking a
subspan, then calls `protocol::Identity::decode`. Identity itself has no HANDLE/WIL/device
discovery dependency. These I/O operations span the operating-system boundary and identity
contract, so they belong to the reusable device component.

Preserve the repository's existing user-mode exception policy for this component:
OS failures use the existing system/runtime errors, and a rejected identity becomes the
existing malformed-response exception with its numeric IdentityError category. The decoder
itself returns typed errors through `std::expected`. Device functions are not `noexcept`.
`main` continues catching and reporting failures with the existing exit behavior. Do not
add a new transport-error taxonomy, connection service object or custom expected replacement
as part of this ownership change.

The CLI-only probe/stress commands remain executable-owned scenarios. Ordinary discovery,
open and query calls use the device component. The malformed-request probe deliberately
retains its raw DeviceIoControl calls so it can exercise invalid wire input; its decoder
call changes to `Identity::decode`. Bounded text formatting stays local to the executable.

### Files and build boundaries

```text
shared/include/sandbox_hwid/protocol/
  identity.hpp          wire fields, constants, errors, request validation, ABI assertions
                        user-mode Identity::decode and private helper declarations
  device_interface.hpp  GUID, IOCTL and device interface contract

client/include/sandbox_hwid/
  device.hpp            public device I/O API
client/src/
  identity.cpp          Identity::decode and private text helper definitions
  device.cpp            discovery, open, query, private Windows helpers
  main.cpp              CLI, formatting and probe/stress scenarios

driver/
  driver.cpp            KMDF callbacks and request handling
  SandboxHwid.vcxproj
  SandboxHwid.inf

tests/
  identity_test.cpp     public decoder, request contract and ABI/type-trait checks
```

Remove `client/include/sandbox_hwid/protocol/validation.hpp`; rename the existing
`client/src/validation.cpp` and `tests/validation_test.cpp` around identity. No standalone
`validation` module or application-wide `errors.hpp` remains. Preserve the product roots.
The library prefix makes public include names distinctive; `protocol` identifies the
shared communication contract. External dependencies remain in their own fetched source
trees/cache, not inside `shared/include/`.

CMake consumption contract:

- Keep the `sandbox_hwid::contract` header target. Its user-mode include surface now
  requires `cxx_std_23`; change the old C++17 usage requirement accordingly. The WDK
  project builds separately and keeps its current language/runtime configuration.
- Replace `sandbox_hwid::validation` with `sandbox_hwid::identity`, a static target for
  `client/src/identity.cpp`. Link the header contract PUBLIC and existing build options
  PRIVATE. It does not publish `client/include` or link WIL/cfgmgr32.
- Add `sandbox_hwid::device`, a static target for `client/src/device.cpp`, publishing
  `client/include`. Link identity and WIL PUBLIC, because its header exposes their types;
  keep cfgmgr32 and build options PRIVATE.
- Link the executable to device and its existing build options. Link identity tests to
  identity, Catch2 and existing test options. Preserve MSVC runtime selection on all
  owned compiled targets, the client manifest, presets and existing dependency pins.

```text
hwid_client --> device --> identity --> contract
                   |
                   +----> WIL (public handle type), cfgmgr32 (implementation)
identity tests ----------> identity
WDK driver --------------> kernel view of shared headers
```

Folder hierarchy and namespace depth remain independent. `protocol` is the shared wire
boundary and `device` is the user-mode I/O boundary; Identity does not get another
`identity` namespace. The pure identity target can be tested without opening a device.

### Reusable standards follow-through

The implementation updates these authored owners and regenerates their packages:

- `.agents/base/contract/domain-design/SKILL.md`: show an intrinsic representation's
  type-owned static decoder and private helpers; make one public boundary-validation path
  the default for this example. Explain that reusable cross-type algorithms and I/O adapters
  can remain free functions in their owning component. Keep passive records distinct from
  invariant-enforcing values; do not claim C.4/C.5 mandate static member placement.
- `.agents/base/contract/structure/SKILL.md`: clarify that public owner prefixes, meaningful
  contract folders, dependency checkouts and target boundaries serve different purposes.
- `.agents/base/contract/style/SKILL.md`: change only if the final examples expose a real
  inconsistency; existing contextual constants, namespaces and private-member rules fit.
- Keep the WDK guard and kernel adaptation in sandbox-specific guidance; kernel policy
  remains outside cpp/gpp/msvc/win32 scope. Update sandbox AGENTS/README/current conventions
  and verification references to the final files and user-mode language requirement.

Regenerate from `.agents/` with `.agents/sync-generated.ps1`; do not author generated
host adapters, marketplace outputs or installed cache copies directly. Preserve existing
canonical skill names, compatibility aliases and the signed provenance history.

### Implementation sequence and acceptance

1. Apply the header/member decoder, remove the free decoder/header and rename the identity
   source/tests. Update consumers to the public decoder; remove response tests that call
   private checks. Preserve all existing behavior checks through the public API.
2. Extract the device component and wire the declared CMake dependencies. Preserve CLI
   behavior, probe semantics, buffer-length checks, RAII ownership and kernel request checks.
3. Reconcile the authored standards and current sandbox documentation, regenerate packages,
   and run the required checks before updating the existing review candidates when authorized.

Implementation acceptance: all nine existing identity cases pass through the public API
(including length extremes, metadata, profile matching, text boundaries and padding);
request validation and both records' traits/layouts remain checked; the real C++23 client
and C++17 WDK Debug/Release targets build; appropriate formatting/static analysis and
required repository generation/route/package/host/scaffold checks pass. Inspect real
target dependencies to prevent WIL/STL from reaching the kernel view. CLI help is a host
smoke check. Device/VM runtime checks retain their existing separate authorization.

### Evidence and limits

The earlier standalone expected probe did not establish WDK library compatibility. Its
actual WDK experiment failed when expected was exposed to the kernel headers; that result
is retained at `C:\Users\tommy\AppData\Local\Temp\cpp-expected-wdk-5o4z399w`.

The final guarded member design above was compiled in an isolated copy at
`C:\Users\tommy\AppData\Local\Temp\cpp-identity-member-design-_wx5oa0k`:

- The adapted nine existing identity test cases passed, with 348 assertions.
- The public device header compiled with the installed WIL/MSVC environment.
- The actual copied WDK project rebuilt in Debug and Release, using its unchanged C++17
  settings and the proposed header. All size/offset assertions and added compiler trait
  assertions for both records passed.
- The temporary standalone test link initially lacked its console-subsystem flag; adding
  that harness setting resolved the link failure. No product workaround or suppressed
  diagnostic was required.

Evidence logs are `host-build.log`, `host-tests.log`, `device-header.log`,
`wdk-Debug.log` and `wdk-Release.log` in that isolated directory. The public header and
identity implementation were prototyped; extraction of device implementations, complete
CMake integration and full project checks remain implementation work. No original sandbox
source was changed, and no driver was signed, installed or loaded.

Primary references supporting the design:

- [C++ class properties](https://eel.is/c++draft/class.prop) and
  [aggregate rules](https://eel.is/c++draft/dcl.init.aggr): private static functions
  do not change the relevant rules for the public data members.
- [Microsoft /kernel](https://learn.microsoft.com/en-us/cpp/build/reference/kernel-create-kernel-mode-binary?view=msvc-170):
  the compiler defines `_KERNEL_MODE`; it supports target-specific conditional compilation.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines):
  record/invariant distinction and small interfaces; type-owned static grouping is the
  selected house preference, not a universal DDD or C++ mandate.

## Progress

- 2026-09-27 behavior-ownership standard is delivered for review in
  [PR #28](https://github.com/tj-agents/cpp/pull/28) at
  `4acf39a766a410bad3b9f914daecb719ae91541f`. The
  authored `cpp:domain-design` addition makes cohesive type ownership a general preference
  rather than a factory-only rule, while retaining free functions for independent or
  cross-type behavior. The change affects `cpp` and the `base`/`cpp-standards` compatibility
  packages; their source manifests have the required patch bumps and generated package
  versions are recorded. Generator freshness, all six route profiles, 11 hook tests,
  marketplace/attester/package contracts, strict Claude validation for the marketplace and
  all nine packages, and the available MSVC and Win32 scaffold acceptance checks pass.
  G++ scaffold acceptance could not run: `bash.exe` is a WSL launcher but no Linux
  distribution is installed (`execvpe(/bin/bash)` fails). Codex's local CLI is unavailable;
  no claim is made for its host validator. The change itself does not alter scaffolds.
- 2026-09-23 implementation delivered to the existing review candidates. Source PR #13
  is at `1229f9d6c355bbf1d11cc2898188429731ffca90`; sandbox draft PR #1 is at
  `d37d333358d6bd0b3cdd67d2bc0db45ac52c7a4e`. Both remote heads were verified.
  Source CI, Ubuntu/Windows attester safety and repository-binding are green on that
  exact source head (runs 35868810729, 35868810733 and 35868808748). Both PR descriptions
  now describe the member decoder/device structure. Local installed cpp guidance matches
  generated source byte-for-byte. Unrelated sandbox edits, including its pre-existing
  header whitespace, remain unstaged. Neither PR is merged. This final plan checkpoint
  is local bookkeeping and does not change the published, validated code candidate.
- 2026-09-23 member-decoder/device implementation completed locally. Identity owns decode
  and a private fixed-extent span text helper; the free decoder/header are removed, device
  operations have their own target, and public headers advertise C++23 to user mode while
  preserving the kernel view. All nine real client tests pass, all three client translation
  units pass clang-tidy, and actual WDK Debug/Release compiler-analysis builds have zero
  warnings/errors. Formatting and the generic C++23 standards example compile pass.
  Source generator/routes, 11 hook tests and 51 source tests pass (one existing optional
  skip); both hosts validate all nine packages. Evidence:
  C:\Users\tommy\AppData\Local\Temp\cpp-member-delivery-6hauk1xc.
  The helper uses span.front() after resolving the C-array/bounds analyzer findings.
  Sandbox unrelated files and the original header whitespace edit remain outside staging.
- 2026-09-23 the independently committed trust-test correction at d580e8c restores both
  protected files to origin/main. Its exact-head repository-binding, CI and attester-safety
  checks are green. The old migration-specific debt entry is resolved and removed; retain
  the separate branch-protection and checkout-upgrade debt. Recheck the new published head.
- 2026-09-23 design completed: type-owned user-mode decoder, private text helper,
  request validator, device API, file layout, target dependencies and standards follow-through
  are specified above. The isolated proposed header/decoder passes 9 tests (348 assertions)
  and real WDK Debug/Release builds with ABI/type-trait assertions. Product source and
  existing PRs remain unchanged by this planning step.
- 2026-09-23 response ownership delivered to [source PR #13](https://github.com/tj-agents/cpp/pull/13)
  and [sandbox draft PR #1](https://github.com/tomjseery/sandbox-hwid/pull/1). Published code
  commits are `73c039cd86299a825ab9f68f56eb11af7234ec05` and
  `977798dd4a45e39b250be0ec53ceb21b90e0a7bd`; remote heads were verified. This plan checkpoint
  follows the source code commit. Unrelated sandbox edits remain local. Neither PR is merged;
  the existing trusted-provenance prerequisite remains with the debt owner below.
- 2026-09-23 response ownership implemented and validated. Required generator/routes, 11 hook
  tests and 51 source tests pass (one existing optional skip). Both hosts accept all nine
  packages; evidence is in `C:\Users\tommy\AppData\Local\Temp\cpp-rules-hosts-fc59do6c`.
  Sandbox client/9 tests, real WDK rebuild/analysis, direct C++17 `/kernel` constexpr checks,
  owned formatting and client clang-tidy pass. Current docs and local cpp guidance are updated.
  MSVC 19.51 rejects valid constexpr reads of implicit zero padding after string literals;
  an isolated reproduction confirms this is independent of validation. Compile-time test
  fixtures now use explicit character initializers; production records are unchanged.
- 2026-09-23 namespace correction implemented and validated for the existing PRs. The shared
  contract uses `protocol`; the type names and ABI remain unchanged. Source generator/routes,
  11 hook tests and 51 source tests pass (one existing optional skip); both hosts accept all
  nine packages. The C++17 guide example compiles. Sandbox client/8 tests, real WDK build and
  analysis, formatting of owned changes, and client clang-tidy pass. Local cpp/msvc guidance
  was refreshed and byte-verified. The prior candidate SHAs below remain historical evidence.
- 2026-09-23 requested correction delivered for review. Source PR
  https://github.com/tomjseery/cpp-agents/pull/13 is updated at
  `45c448cdf3a9f653a9b9348502b0513e06b3f4fe`; the sandbox companion draft is
  https://github.com/tomjseery/sandbox-hwid/pull/1 at
  `52e8632fc002111145501859e9d52c4c00cad170`. Both remote branch SHAs were verified after
  pushing, and the existing source PR description was rewritten for the final change.
  Generated-package CI and Ubuntu/Windows attester-safety jobs pass on that source head;
  repository-binding still fails at the documented provenance gate. Neither PR is merged.
  The source workspace's final plan checkpoint is local bookkeeping after the published
  candidate; it does not change the validated source or require another CI-triggering push.
- 2026-09-23 correction validation: all required source checks pass. Generator is current at
  220 files / 16 definitions; six route profiles pass; 11 hook tests and 51 source tests
  pass with one existing optional live-source skip (61 executed passes total). This includes
  marketplace, attester, generator safety and both scaffold suites. Claude strictly validates
  the marketplace and nine packages; Codex installs all nine into an isolated profile.
  Host evidence: `C:\Users\tommy\AppData\Local\Temp\cpp-identity-host-validation-dlisbfjd`.
  The new C++17 example compiles with G++ `-Wall -Wextra -Werror -pedantic`; constexpr
  validation and standard-layout/trivial-copy/aggregate assertions pass.
- 2026-09-23 sandbox correction: client build and all 8 CTests pass; WDK C++17 `/kernel`
  build and `/analyze` rebuild each have zero warnings/errors. All seven C++ files pass
  clang-format and both client translation units pass clang-tidy with no owned diagnostics.
  All original data fields, field order, GUID and IOCTL compare unchanged; sizes, every
  metadata offset and the original text offsets are asserted. Host trait checks cover both
  records. Client help succeeds; driver is `NotSigned`. Current logs and hashes are recorded
  in the sandbox verification document. No driver/runtime actions occurred.
- 2026-09-23 local capability refresh: reinstalled only the already-selected `cpp` 0.2.0
  through Codex's supported installer in the sandbox directory; installed style/design
  bytes match generated source and the global marketplace registration is unchanged.
- 2026-09-23 provenance diagnosis: the earlier migration changed two blobs pinned by the
  trusted attester on `main` (marketplace tests and CI). Missing attestation is therefore
  not resolved by simply rerunning the old script. The separate reviewed trust-pin update
  and objective completion condition are owned by
  [the provenance debt entry](../../TECH_DEBT.md#review-provenance-pins-for-the-canonical-capability-migration).
  Preserve this gate when updating PR #13; do not weaken it or post an unverified success.
- 2026-09-23 correction resumed by the current Codex session at Tommy's request. The source
  checkout is clean at `f2f4ecd1082a2e7d7f71ac1e9abed062942ebb15`; PR #13 is open at that
  exact head: https://github.com/tomjseery/cpp-agents/pull/13. Its generated/attester tests
  passed, but the repository-binding provenance check failed; inspect and resolve or report
  the actual remaining gate when updating the candidate. No merge has occurred.
- 2026-09-23 sandbox HEAD is `881769bc37f03af32cd18d4a74bcc644c17abee5` on
  `Refactor/Canonical-Structure`, with no open PR. Preserve unrelated dirty
  `docs/next-session.md`, `docs/winwrap-integration.md`, `.codex/`, both handoff prompt files,
  and `nvim.log`. This correction owns only the relevant source/header moves, consumers,
  ABI checks, build header paths and current design/verification documentation.
- 2026-09-22 handoff checkpoint: Source checkout remains
  `C:\Users\tommy\AppData\Local\Temp\cpp-agents-explicit-wire-types`, branch
  `fix/explicit-wire-integer-types`, HEAD `e0304dfcba2db5263eb9822e2b06e6706f311165`.
  All design/migration edits described above remain uncommitted. A fresh GitHub query
  for every PR state on this head branch returned `[]`; no PR for this branch was found.
  This session has not published or merged these changes. The source retains the earlier
  exact-width conventions commit, which must not be lost.
- 2026-09-22 handoff checkpoint: The lab remains
  `C:\Users\tommy\source\repos\sandbox-hwid`, branch `Refactor/Canonical-Structure`,
  HEAD `03a2ffef8640508c2bf664802507030c3571141c`. Its design application is already
  implemented and validated locally. The latest chat showed the scheduling examples from
  the skill plus a mutable `Appointment` example to explain entities. Those teaching
  examples are not a proposal to add appointments, entities, factories, or a domain layer
  to the HWID protocol.

## Earlier Claude transfer

- Transfer requested by Tommy; target harness is Claude Code with its configured default
  model. The earlier `gpt-6-astra` selection concerned the independent Codex research pass;
  it does not override this newer explicit Claude request.
- Launch directory is the source checkout above. Prompt file is
  `C:\Users\tommy\AppData\Local\Temp\cpp-design-claude-handoff.txt`.
- The parent submitted one packaged `machine:handoff-claude` launch and released writing
  ownership on its success message. The resulting commits and PR are observed above.
  The current user request returns ownership of the bounded correction to this Codex session;
  do not launch another owner for it.
- Preserve pre-existing lab changes in `docs/next-session.md`, `docs/winwrap-integration.md`,
  `.codex/agents/`, both `BASE_AGENTS_*PROMPT.md` files, and `nvim.log`. Do not stage them
  accidentally with this work. The unrelated temporary patch seen earlier is absent from
  the latest status; this session did not remove it.
- This task owns the lab's `.agents/skill-routes.json`, `AGENTS.md`, `README.md`,
  `shared/include/sandbox_hwid/protocol/identity.hpp`,
  `client/include/sandbox_hwid/protocol/validation.hpp`, `client/src/validation.cpp`,
  `client/src/main.cpp`, `driver/driver.cpp`, `tests/validation_test.cpp`,
  `docs/conventions.md`, `docs/verification.md`, and the newly added `.codex/config.toml`.
  The latter is machine-local; preserve existing agent files and do not publish its
  absolute temporary source path as a portable project setting.

## Earlier execution evidence

- 2026-09-22: Implementation and local delivery completed. Independent generator review found
  no lost published skill paths, unresolved package references, or resource-link failures.
  Final required PowerShell generator check reports 220 current files / 16 definitions.
  Claude Code 2.1.278 strictly validated the marketplace and all nine packages. Codex CLI
  0.155.1 installed all nine into an isolated profile. Final G++ scaffold matrix passed
  all five tests, including actual C++20/23 builds; MSVC matrix passed all three tests.
  All eight Python suites passed: 61 tests passed, one pre-existing optional live-source
  comparison skipped. Historical signed provenance is unchanged and its pinned checks passed.
- 2026-09-22: Sandbox HWID renames and design rationale completed. Client build and 8/8
  tests pass; real WDK 10.0.28000.0/KMDF 1.31 build and `/analyze` rebuild have zero warnings
  or errors; clang-format checks all seven C++ files and clang-tidy checks both client
  translation units. Request/response sizes stay 16/160 bytes with text offsets 16/64/112.
  ABI declarations, error mappings, protocol version, GUID and IOCTL are unchanged.
  Detailed logs and artifact hashes are recorded in the lab's `docs/verification.md`.
- 2026-09-22: Initial global per-command local installs byte-verified at 0.2.0, but the
  shared cache later contained 0.1.0 again. Diagnosed the effective source selection and
  added a lab-only `.codex/config.toml` local marketplace setting. Ordinary lab-directory
  install and subsequent list commands, with no source overrides, now resolve `cpp`,
  `msvc`, and `win32` 0.2.0 and installed payload bytes match. The global Git source and
  revision are unchanged; legacy cpp-agents plugins are disabled only in the lab profile.
  Existing `.codex/agents` and unrelated dirty files were preserved. A concurrently appearing
  `.tmp-model-routing-debt.patch` was left untouched.
- 2026-09-22: Delivery is local source, generated packages, installed lab selection, and
  validated lab code. No remote publication or Git commit was performed. The lab's local
  source setting depends on this checkout remaining available until the release is published;
  its removal and revalidation procedure is documented in `docs/conventions.md`.
  No driver loading, installation, signing-policy change, VM operation, or WinWrap change
  was performed. Guest/runtime and fresh INF/CAT evidence remain outside this task.
- 2026-09-22: Independent research completed against the C++ Core Guidelines (C.2/C.4/C.5,
  construction, F.8, NL.8), Evans' DDD Reference, Abseil factory guidance, WG21 P0323R12,
  Sean Parent's value-semantics material, Gary Bernhardt's functional-core/imperative-shell
  explanation, and Boost.URL's production API. Primary-source links and concise rationale
  live in the canonical `domain-design/SKILL.md`. The earlier Brian Will reference was not
  needed as independent evidence. Review clarified that Evans recommends immutable DDD
  Value Objects; allowing mutable C++ values is an explicit broader house adaptation.
- 2026-09-22: All 15 existing capabilities renamed; `cpp:domain-design` added. Canonical
  packages are 0.2.0; legacy packages received patch increments. Generator now resolves
  qualified source identities and produces 220 files from 16 definitions. Canonical old
  names redirect locally until 2027-03-31; compatibility packages retain old names.
  Fixed the discovered G++ packaged script-link relocation alongside the MSVC mapping.
- 2026-09-22: Observed green checks so far: generator safety 17/17; marketplace 15 passed
  with one optional live-source comparison skipped (pinned signed verification passed);
  attester 4/4; hooks 11/11; route/structure 6/6; route self-test across six profiles;
  MSVC scaffold acceptance 3/3. Some process launches required sandbox escalation.
  G++ scaffold validation and strict Claude validation are still running. Codex installed
  all nine packages successfully into the isolated temporary validation profile.
- 2026-09-22: Extracted the complete C++23 example from the skill and compiled it with
  G++ using `-Wall -Wextra -Werror -pedantic`; runtime checks passed for valid/invalid
  construction, preserved input, overlap, and extreme integer shifts. Independent review
  found no example correctness issue. A separate generator review is in progress.
- 2026-09-22: Sandbox HWID application started after local package generation and checks.
  The existing dirty files remain outside the edit lease. Parent owns only lab guidance
  and route migration; worker owns protocol/client/kernel naming, relevant docs, and host
  validation. No driver execution or VM operation is authorized.
- 2026-09-22: Resumed in the requested cpp-agents checkout with `engineering:plan-execution`
  in its runtime-unavailable mode. Existing branch is `fix/explicit-wire-integer-types`;
  the pre-existing commit and Sandbox HWID's unrelated dirty files are preserved.
  Independent source review is in progress. Generator migration uses qualified source
  identities, explicit flat host-adapter names, and generated dated compatibility aliases.
  Research and authored guidance remain with the parent; independent workers own generator
  compatibility, routes/tests, and read-only Sandbox HWID evidence.
- 2026-09-22: Research reconciled against Eric Evans' DDD reference, Brian Will's procedural
  programming/state guidance, and C++ Core Guidelines C.1-C.5. Existing cpp-agents source and
  Sandbox HWID identity flow inspected. No deliverable edits or runtime actions performed yet.
- 2026-09-22: The first default-model handoff was launched and then stopped by Tommy before
  implementation. Tommy explicitly selected `gpt-6-astra` for a stronger independent research
  pass; the replacement handoff must use that model rather than inheriting the CLI default.

## Next Steps

The agreed implementation, standards update, local installation refresh, validation and
existing-PR updates are complete. Review candidates are [source PR #13](https://github.com/tj-agents/cpp/pull/13)
and [sandbox draft PR #1](https://github.com/tomjseery/sandbox-hwid/pull/1), with exact heads
and successful checks recorded above. No refactor work remains for this request.

Neither PR is selected for merging by this implementation request. A later authorized
release can replace the lab's existing local marketplace override with the Git source.
Driver signing, loading, installation, VM checks and unrelated WinWrap work remain outside
this delivery.
