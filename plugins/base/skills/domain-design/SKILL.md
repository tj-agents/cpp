---
name: domain-design
description: Model C++ records, invariant-bearing values, entities, operations, typed errors, and stateful boundaries using DDD vocabulary without imposing an object-oriented architecture.
kind: contract
domain: cpp
---

# Domain design in C++

Use this skill when choosing data representations, operations, validation, or component
boundaries. Start with the problem's vocabulary and actual rules. A protocol utility may
need only records and functions. Do not create a domain layer merely because this skill
was loaded. `base:cpp-style` owns spelling and formatting; `base:cpp-structure` owns project layout.

## Choose the representation from its contract

The C++ Core Guidelines C.2, C.4, and C.5 guide this baseline: independently editable
data belongs in a `struct`; an invariant requiring controlled access belongs in a
`class`; non-member helpers belong in the associated namespace. C.4 favors a small
member interface when privileged access is unnecessary. The type-owned static helpers
below are a deliberate house preference for grouping and discovery, not a C.4 mandate.
Resource-owning classes also enforce lifetime contracts. Neither keyword implies inheritance.

A passive input record can contain invalid input. Validation decides whether to accept it;
it does not turn the record into a permanently validated value. An encapsulated value must
remain valid through construction, assignment, moves, and every public operation. A
validator followed by unrestricted field writes does not provide that guarantee.

| Role | Shape | Reason to introduce it |
|---|---|---|
| Passive record | Public fields, with type-owned static validation or associated helpers as appropriate | Transfer or collect data |
| Invariant-bearing value | Small class, controlled construction, appropriate value operations | Make an actual invalid state unrepresentable through the public API |
| Entity | Stable domain identity plus explicit permitted transitions | Track the same thing while its attributes change |
| Stateful adapter | RAII ownership and a small operational interface | Own a file, connection, device, transaction, or other external resource |

## DDD vocabulary without a mandatory class hierarchy

Evans distinguishes entities by continuing identity and value objects by their attributes.
Aggregates establish consistency boundaries; a domain service names an operation that
does not fit an entity or value object. These are modelling roles, not required C++ base
classes, suffixes, folders, or dependency-injection registrations.

For example, two appointments with equal times can still be different appointments.
An `AppointmentId` identifies an entity; a `TimeWindow` describes a value. Define equality
from that meaning: equal window bounds can mean equal values; equal entity identifiers
mean the same entity, not necessarily an identical state snapshot. Do not default entity
equality across all its fields without deciding which question it answers.

Use an aggregate only when several pieces of state must obey a shared rule at one update
boundary. Do not manufacture repositories or aggregate roots around a read-only message.
The C++ mapping here is a house design decision; DDD does not prescribe these C++ spellings.

## Place operations with their actual owner

Prefer `IdentityRequest::validate(request)` for a stateless contract check that belongs to one
record type and benefits from discovery on that type. A static member has no implicit
`this` object; the checked record remains an explicit input. Static is not a
purity guarantee: side effects still depend on the implementation. An ordinary `const` member
can also express a check of the receiver. Public fields do not forbid either spelling.

Use an associated free function for an independent algorithm, an operation spanning
several types, or an adapter whose dependencies do not belong in the type's contract.
C.5 guides where such free helpers live; it does not require every record operation to
be free. A protocol validator is not automatically a DDD Domain Service, and putting it
on a struct does not make that struct an invariant-enforcing Value Object.

This C++17 example groups a check with a passive record without adding a constructor:

```cpp
#include <cstddef>
#include <cstdint>

namespace device::protocol {

inline constexpr std::uint32_t protocol_version{1};

enum class IdentityRequestError { none, version, reserved };

struct IdentityRequest {
    std::uint32_t version;
    std::uint32_t reserved;

    /// Check a complete object copied from the wire before accepting its contents.
    [[nodiscard]] static constexpr IdentityRequestError
    validate(const IdentityRequest& request) noexcept {
        if (request.version != protocol_version)
            return IdentityRequestError::version;
        if (request.reserved != 0)
            return IdentityRequestError::reserved;
        return IdentityRequestError::none;
    }
};

static_assert(sizeof(IdentityRequest) == 8);
static_assert(offsetof(IdentityRequest, reserved) == 4);

} // namespace device::protocol
```

Ordinary static or non-virtual member functions add no per-object storage and, by
themselves, do not change standard-layout, trivial-copyability or aggregate status.
Keep size and significant-offset assertions for every shared binary contract, plus
appropriate type-trait checks in targets that support them. DDD and successful runtime
validation do not check padding, field order or ABI compatibility. Standard-layout
alone does not fix a cross-platform wire format. Preserve the actual compiler/ABI and
restricted-runtime requirements; do not introduce library dependencies merely to place
an operation on a type. The record's public fields remain editable after validation.

## Keep validation and decoding with their owner

Give a type one owner for its rules and error vocabulary. When a representation is part
of that type's own contract, prefer a static `Identity::decode(bytes, requested_profile)`
or `parse(text)` entry point. A definition in `identity.cpp` remains a member of Identity;
it does not need to be inline or require a separate decoder service class.

- The type's API header declares its errors beside the type. A dedicated error header is
  appropriate when that same component has enough shared vocabulary to justify one;
  a generic `validation.hpp` or application-wide `errors.hpp` should not own unrelated rules.
- Validate untrusted input at the entry boundary: check framing/length before copying or
  converting, then check content before returning success. The returned value owns its data
  unless the API explicitly promises a view and documents the required source lifetime.
- Keep checks used only by that operation private. A local helper is fine; a named
  type-specific helper can be a private static member with its definition in the owning
  `.cpp`. Public data plus private functions is valid for a passive struct.
- Expose a separate `validate(record)` only when callers actually need to check existing
  records. Do not add a second public operation merely to split the steps inside a decoder.
- An adapter for an external representation or an operation spanning several types belongs
  in its own component. It delegates to the owning rules/factory instead of duplicating them.
  Device discovery, resource acquisition and I/O stay with the device boundary.

This complete C++23 example describes an agreed native binary ABI. Producers and consumers
must agree on layout and byte order; an independent cross-platform format needs explicit
field encoding/decoding. The declarations belong in `identity.hpp` and the non-inline
method definitions in `identity.cpp`:

```cpp
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <expected>
#include <span>
#include <type_traits>

namespace device::protocol {

inline constexpr std::uint32_t baseline_profile{0};
inline constexpr std::uint32_t alternate_profile{1};
inline constexpr std::size_t text_capacity{16};

enum class IdentityError { length, profile, text };

struct Identity {
    std::uint32_t profile;
    char serial[text_capacity];

    /// Decode one record using the producer and consumer's agreed native ABI.
    [[nodiscard]] static std::expected<Identity, IdentityError>
    decode(std::span<const std::byte> bytes, std::uint32_t requested_profile) noexcept;

private:
    static bool valid_text(std::span<const char, text_capacity> text) noexcept;
};

std::expected<Identity, IdentityError>
Identity::decode(std::span<const std::byte> bytes,
                 std::uint32_t requested_profile) noexcept {
    if (bytes.size() != sizeof(Identity))
        return std::unexpected{IdentityError::length};

    Identity record{};
    std::memcpy(&record, bytes.data(), sizeof(record));
    if (record.profile != requested_profile ||
        (record.profile != baseline_profile && record.profile != alternate_profile))
        return std::unexpected{IdentityError::profile};
    if (!valid_text(record.serial))
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

static_assert(sizeof(Identity) == 20);
static_assert(offsetof(Identity, serial) == 4);
static_assert(std::is_standard_layout_v<Identity>);
static_assert(std::is_trivially_copyable_v<Identity>);
static_assert(std::is_aggregate_v<Identity>);

} // namespace device::protocol
```

Success is carried by `std::expected`, so this error enum has no `none` member.
The private boolean helper supplies one text rule; the public decoder preserves typed
failures. Keep `return terminated`: reaching the end without a terminator is invalid.
Runtime byte decoding does not need constexpr helpers. Preserve compile-time validation
where a real consumer uses it; test private rules through the public operation.

Respect each consumer's actual language and library baseline. A public header exposing
`std::expected` requires C++23, and its build target must propagate that requirement.
Do not let grouping force unsupported dependencies onto another runtime. A project may
explicitly define different APIs for separate target programs while sharing a data layout;
such adaptations belong in that project's guidance, with identical definitions across
translation units within each program and verified ABI assertions. Conditional data fields
or ad hoc per-file feature switches are not an ownership mechanism.

## Records, factories, transformations, and free functions

This complete C++23 example separates untrusted input from a valid daily time window.
The model deliberately uses minutes within one day; it is not a time-zone or calendar API.

```cpp
#include <expected>

namespace calendar {

struct WindowRequest {
    int start_minute{};
    int end_minute{};
};

enum class WindowError { invalid_bounds, outside_day };

class TimeWindow {
public:
    [[nodiscard]] static std::expected<TimeWindow, WindowError>
    create(int start_minute, int end_minute) noexcept;

    [[nodiscard]] int start_minute() const noexcept { return start_minute_; }
    [[nodiscard]] int end_minute() const noexcept { return end_minute_; }

    /// Return a shifted value; reject a result outside this day.
    [[nodiscard]] std::expected<TimeWindow, WindowError>
    shifted_by(int minutes) const noexcept;

    bool operator==(const TimeWindow&) const = default;

private:
    static constexpr int minutes_per_day{24 * 60};

    TimeWindow(int start_minute, int end_minute) noexcept
        : start_minute_{start_minute}, end_minute_{end_minute} {}

    int start_minute_;
    int end_minute_;
};

inline std::expected<TimeWindow, WindowError>
TimeWindow::create(int start_minute, int end_minute) noexcept {
    if (start_minute < 0 || start_minute >= end_minute ||
        end_minute > minutes_per_day)
        return std::unexpected{WindowError::invalid_bounds};
    return TimeWindow{start_minute, end_minute};
}

inline std::expected<TimeWindow, WindowError>
TimeWindow::shifted_by(int minutes) const noexcept {
    // Check before addition, including for extreme int inputs.
    if (minutes < -start_minute_ || minutes > minutes_per_day - end_minute_)
        return std::unexpected{WindowError::outside_day};
    return TimeWindow{start_minute_ + minutes, end_minute_ + minutes};
}

/// Whether two half-open windows share any time; touching endpoints do not overlap.
[[nodiscard]] inline bool overlaps(const TimeWindow& left,
                                   const TimeWindow& right) noexcept {
    return left.start_minute() < right.end_minute() &&
           right.start_minute() < left.end_minute();
}

} // namespace calendar
```

`WindowRequest` permits incomplete or invalid input. `TimeWindow::create` either returns
a valid value or a typed error; there is no public default constructor or later `init`
step. `shifted_by` preserves the original and uses the private representation.
`overlaps` needs only the public contract, so it is a free function in `calendar`.

Use `create` for fallible construction when that name is sufficient. Prefer a more
specific verb such as `parse`, `decode`, or `open` when it describes the work better.
Ordinary constructors remain appropriate for infallible construction or a project's
established exception policy. Do not require heap allocation or a factory class.

Name immutable transformations for their meaning: `shifted_by`, `normalized`, or
`rescheduled`. A `with_title` operation is reasonable when it means exactly a copy with
one title replacement, but `with_x` is not a universal C++ convention. If a replacement
can break the invariant, return an error or use the established exception policy.

Evans recommends immutable DDD Value Objects. C++ value semantics is broader and does
not require an immutable interface; permitting mutable values here is an explicit house
adaptation when appropriate for the model. A locally owned
`std::vector` can mutate while copies remain independent. Prefer immutable domain
values when they simplify reasoning; allow controlled mutation when it fits the
operation and measured costs. Avoid `const` data members merely to simulate immutability:
they can needlessly disable assignment and useful move operations. Specify any valid
moved-from state and avoid returning views into destroyed temporaries.

## Keep decisions separate from external effects

Make core calculations depend on explicit values. Read the clock, configuration, and
external data at the boundary, then pass the needed facts into the calculation. A core
function can return a decision or proposed transition for the boundary to apply.
Predictable transformations are easier to test than functions that implicitly consult
global state, as illustrated by Bernhardt's functional-core/imperative-shell design.

A stateful adapter still has a purpose. For example, `calendar::storage::AppointmentStore`
can own a connection and offer `load` and `save`; `calendar::overlaps` does not need that
connection. Application orchestration loads a snapshot, computes the decision, and
persists it. Keep atomicity and version checks at the persistence boundary: a pure
calculation alone does not prevent two concurrent bookings from racing.

Keep boundaries coarse enough to reflect real ownership. Do not create a service class
for each function, a generic manager for unrelated resources, or an interface for a
single trivial operation. A DDD service that needs no state can be an associated free
function. Use a class when resource lifetime, invariants, or an actual polymorphic
contract justify it.

## Error and naming contracts

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

Use clear concept nouns, role suffixes only where they disambiguate, and operation verbs:
`Identity`, `IdentityRequest`, `IdentityRequestError`, `IdentityError`,
`IdentityRequest::validate`, `Identity::decode`, and `query_identity`. These spellings are house examples,
not a claim that all C++ libraries use the same casing or factory name. Avoid repeating
a type's name in an operation when its class or namespace already provides that context.

Start with the owning project/library namespace. Add nested namespaces for meaningful
subsystem or contract boundaries, not automatically for each feature, folder, or domain
noun. For example, `sandbox_hwid::protocol::Identity` and `IdentityRequest` name records
in the shared client/driver wire contract. That contract justifies `protocol`; the noun
`Identity` does not by itself require an enclosing `identity` namespace. Retain the
concept names instead of renaming them to fit a preferred namespace hierarchy.

Namespace depth is not a measure of scalability. Establish known ownership and dependency
boundaries through public APIs and build targets; folders and namespaces need not mirror
one another. Preserve the wire ABI and use explicit mapping if a separate behaviour-bearing
model becomes useful.

## Evidence and deliberate house choices

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines):
  C.2/C.4/C.5 guide representation and function placement; C.40/C.41 address invariants
  and construction; F.8 motivates pure functions; SF.20 connects namespaces to logical
  structure; NL.8 treats naming as a consistency choice.
- [C++ class properties](https://eel.is/c++draft/class.prop) and
  [aggregate rules](https://eel.is/c++draft/dcl.init.aggr): ordinary static/non-virtual
  member functions do not add object state or disqualify these record properties.
- [Eric Evans, DDD Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf):
  Entities, Value Objects, Services, Aggregates, and Factories supply domain vocabulary.
  Applying that vocabulary without a mandatory `domain` folder is our C++ mapping.
- [Abseil, factory functions](https://abseil.io/tips/42):
  a production-library rationale for complete construction instead of two-stage initialization.
  This does not require importing Abseil or its pointer-returning examples.
- [WG21 P0323R12](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p0323r12.html):
  rationale and specification for a value-or-error vocabulary type.
- [Sean Parent, Value Semantics](https://sean-parent.stlab.cc/presentations/2013-09-24-value-semantics/value-semantics.pdf):
  value-oriented design complements resource ownership and does not mean all objects
  must expose immutable APIs.
- [Gary Bernhardt, Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell):
  an explicit separation of calculations and external effects, adapted here to C++.
- [Boost.URL parsing](https://www.boost.org/doc/libs/1_83_0/libs/url/doc/html/url/ref/boost__urls__parse_uri.html)
  and [its mutable URL example](https://github.com/boostorg/url):
  real library APIs combine free parsing functions, typed results, observers, and mutation.
  Their spelling is evidence of variety, not a dependency recommendation.

The short plugin identifiers, PascalCase types, snake_case functions, `create` default,
optional `with_x`, type-owned static validation and a project namespace with meaningful
nested boundaries are deliberate house choices.
They are not requirements of DDD or the C++ language.
