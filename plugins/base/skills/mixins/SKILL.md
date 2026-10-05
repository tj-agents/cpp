---
name: mixins
description: Design, organize, and test C++ mixins, CRTP behavior providers, and policy-style composition. Use for inheritance-based behavior composition; this is a language and design-pattern capability, not domain-driven design.
kind: convention
domain: cpp
---

# C++ mixins and behavior composition

Mixins are a general C++ composition pattern. They do not imply domain-driven design, a
domain layer, or a particular application architecture. Load this skill when behavior is
assembled through CRTP, policy bases, or related inheritance-based providers.

Use a mixin only when inheritance expresses mechanical behavior composition. Prefer an
ordinary member, free function, or owning component when behavior needs independent
identity, shared mutable state, runtime replacement, or a lifetime separate from the host.

## Name the behavior, not the mechanism

Name a provider for the behavior or role it adds, not for the fact that it is a mixin or
uses inheritance. Use an `-able` name selectively when it expresses a real capability,
such as `FileDroppable`. Use natural role names for observed events and protocol
responsibilities, such as `ConnectionObserver` and `CommandRouter`; do not impose one
suffix on every provider.

## Choose `struct` or `class` from the provider's contract

Use a transparent `struct` when the provider is stateless and has no hidden invariant.
Use a `class` when it owns controlled state or a lifetime rule. Inheritance alone decides
neither keyword.

This capability mixin has no data and leaves the reaction on its host:

```cpp
#include <string_view>
#include <variant>

struct FileDrop { std::string_view path; };
struct Command { std::string_view name; };
using Event = std::variant<FileDrop, Command>;

template<class Host>
struct FileDroppable {
    [[nodiscard]] bool try_handle(const Event& event) {
        const auto* drop = std::get_if<FileDrop>(&event);
        if (drop == nullptr)
            return false;

        static_cast<Host&>(*this).on_file_drop(drop->path);
        return true;
    }
};
```

A provider with a hidden invariant is different even if consumers compose it through
inheritance:

```cpp
#include <stdexcept>

class RetryBudget {
protected:
    explicit RetryBudget(int attempts) : remaining_{attempts} {
        if (attempts <= 0)
            throw std::invalid_argument{"attempts must be positive"};
    }

    [[nodiscard]] bool consume_attempt() noexcept {
        if (remaining_ == 0)
            return false;
        --remaining_;
        return true;
    }

private:
    int remaining_;
};
```

The `class` protects the construction rule and remaining budget. Do not expose its state
merely to make it resemble a stateless provider, and do not turn the stateless provider
into a `class` merely because it is a base.

## Make routing precedence part of the contract

Mixin order can change public behavior. A short-circuit chain is explicitly
first-match-wins:

```cpp
template<class Host>
struct CommandRouter {
    [[nodiscard]] bool try_handle(const Event& event) {
        const auto* command = std::get_if<Command>(&event);
        if (command == nullptr)
            return false;

        static_cast<Host&>(*this).on_command(command->name);
        return true;
    }
};

class Editor : public FileDroppable<Editor>, public CommandRouter<Editor> {
public:
    [[nodiscard]] bool dispatch(const Event& event) {
        return FileDroppable<Editor>::try_handle(event) ||
               CommandRouter<Editor>::try_handle(event);
    }

    void on_file_drop(std::string_view path);
    void on_command(std::string_view name);
};
```

The left operand runs first and the right operand runs only when the first returns false.
If two providers can match the same event, define which one owns it, narrow the predicates,
or make precedence explicit in the public contract. Do not let base-list order or an
incidental fold-expression order become undocumented policy. Distinguish observers,
which may all need notification, from handlers or routers, which may consume an event.

Review every composition for these hazards:

- overlapping match conditions and first-match-wins shadowing;
- an ordering assumption hidden in a type alias, base list, or parameter pack;
- one provider reading state that another provider must initialize or preserve;
- references, callbacks, or views that outlive the host or another provider's state;
- construction and destruction order when several bases own resources.

Prefer an explicit host operation when providers interact. If two behaviors must share a
state machine or lifetime invariant, one owning component is often clearer than nominally
independent mixins with hidden coupling.

## Organize by the behavior's owner

Group headers and sources by the resource, protocol, subsystem, or other stable owner they
implement. For example:

```text
include/acme/editor/file_drop.hpp
include/acme/protocol/command.hpp
src/editor/file_drop.cpp
```

The language mechanism does not automatically require a `mixins/` directory. Create that
directory only when mixins themselves form a real public library boundary; do not create
placeholder types or public APIs merely to make a mechanism-named directory look complete.

A public template may include support headers because its definition must be available to
consumers. Put implementation-only support under an owner-prefixed path such as
`<acme/detail/file_drop_dispatch.hpp>` when useful. `detail/` means the declaration has no
supported compatibility contract; it is not access control, and consumers can still name
it at their own risk. Physical inclusion by a public template does not make detail names
supported API.

Keep paths independent from C++ namespaces. A folder can help humans navigate a family of
providers without adding a namespace. Add a namespace only when it names a real library,
subsystem, or protocol ownership boundary; do not mirror `detail/` into namespace spelling
as a substitute for documenting unsupported status.

## Contain implementation macros

A macro cannot live in a C++ namespace. Give every library macro a library-specific
prefix, define an implementation macro only around the expansion that needs it, and
`#undef` it before the public header finishes. Namespace qualification does not prevent
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

A public header that genuinely needs both the enum and stable display names contains each
expansion locally:

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
`detail/`, require the setup macro with `#error`, and never expose that macro as supported
API. Prefer an ordinary `constexpr` table, template, or function when repeated
preprocessing is unnecessary.

## Test the composed behavior and public headers

Test through the host's public operation rather than only instantiating provider templates.
Cases should prove:

- each non-overlapping event reaches its intended behavior;
- an unhandled event falls through to the next provider;
- overlapping conditions follow the documented first-match rule;
- reordering providers changes behavior only where the public contract permits it;
- shared or provider-owned state moves through the intended transitions; and
- callbacks, references, views, and resource-owning bases do not outlive their owners.

A compile-only assertion can prove composition constraints, but it cannot prove which
handler ran, whether a later handler was shadowed, or whether coupled state and lifetimes
remain valid.

Give a public header with substantial template or preprocessor implementation a minimal
translation-unit compile check. Compile it with only the public target's advertised usage
requirements so the check detects missing direct includes, include-order dependencies,
and leaked macros:

```cpp
#include <acme/event_kind.hpp>

#if defined(ACME_DETAIL_EVENT)
#error "event_kind.hpp leaked an implementation macro"
#endif

int main() {}
```

Do not include an unsupported repeatable fragment in a consumer-facing header test: it
deliberately requires its setup macro and is not a standalone API. When the fragment itself
warrants a focused internal test, define the setup macro, include the fragment, `#undef`
the macro, and repeat with a different definition to exercise its intended contract.
