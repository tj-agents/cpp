# What I know — C++ (Tommy)

A running inventory of which C++ concepts I've actually learned, kept so anyone
(me, or Claude) can calibrate to my level. Mostly tracks The Cherno's C++ series.

Legend: 🟡 = seen it but shaky.

## Comfortable with

**Mental model / tooling**
- How C++ works, the compiler, the linker, translation units
- Header files (declaration vs definition), `#include`
- Debugging with breakpoints

**Core language**
- Variables, functions, conditions/branches, loops, control flow (`break`/`continue`/`return`)
- Uniform initialization with `{}` — avoids most vexing parse; preferred over `()` for constructors
- Pointers, references
- `const`, `mutable`
- Ternary operator
- `auto`
- Implicit conversion & the `explicit` keyword
- Macros, namespaces

**Classes / OOP**
- Classes, structs, classes vs structs, how to write a class
- Constructors, destructors, member initializer lists, `this`
- `static` (free functions/vars, and for classes)
- `enum`
- Inheritance, `virtual` functions, interfaces (pure virtual), visibility
- Operator overloading
- Singletons

**Memory & lifetime**
- Object lifetime (stack/scope), object creation/instantiation
- `new`, stack vs heap
- Smart pointers (`unique_ptr`, `shared_ptr`, `weak_ptr`)
- The arrow operator
- Copy constructors / copying
- **lvalues vs rvalues** — value categories; "rvalue = temporary about to die"
- **rvalue references (`&&`)** — and how copy-vs-move overloads get selected by value category
- **Move semantics** — copy = deep-duplicate the resource; move = steal the pointer and leave the source empty-but-valid (null it to avoid a double free)
- **`std::move`** — just re-tags an lvalue as an rvalue (a cast); generates no code, doesn't move anything itself — it just makes the move ctor get picked
- **Move constructor** — `T(T&&) noexcept`: steal the resource, null out the source. `noexcept` matters so `std::vector` will use it
- **Ownership as a convention** — C++ has no compiler-enforced ownership (unlike Rust); it's RAII + discipline. `unique_ptr` = single owner via `= delete`d copy + move-only; the same `= delete` trick makes any class "move-only"
- Local static
- Casting, dynamic casting
- Tracking memory allocations

**Containers, strings, generics**
- Arrays, `std::array`, `std::vector` (+ optimizing its use), multidimensional arrays
- Sorting
- How strings work, string literals, small string optimization
- Templates
- Function pointers, lambdas

**Modern C++ / std types**
- Structured bindings
- `std::optional`, `std::variant` (multiple types in one var), `std::any`
- Multiple return values
- `std::string_view` (C++17) — non-owning view of a string; pointer + length, no heap allocation. Use instead of `const std::string&` when you don't need ownership.
- `std::span<T>` (C++20) — non-owning view over any contiguous array; same idea as `string_view` but for any type. Avoids raw pointer arithmetic.
- `std::expected<T, E>` (C++23) — union of a success value `T` and an error `E` with a bool flag. `return {}` = success (calls default ctor, sets `_M_has_value = true`). `return std::unexpected(e)` = failure. Supports monadic chaining via `.and_then()` / `.or_else()`.
- `std::ignore` (C++11, `<tuple>`) — discard a `[[nodiscard]]` return value on purpose. Equivalent to `_` in Rust/C#.
- `[[nodiscard]]` (C++17) — attribute that makes the compiler warn if you ignore the return value of a function.

**Concurrency / performance (lightly)**
- Threads, timing, `std::async`, benchmarking

**Testing**
- xUnit-style testing (C# background) — test cases, assertions, setup/teardown
- Moq (mocking), WebApplicationFactory (integration tests)
- No C++ testing experience yet — Catch2 is the framework used here

## Seen but shaky 🟡

- **IIFE lambda** — `[]() { /* multi-line setup */ }()` — immediately invoked lambda. Used to compute a value that needs multiple statements and assign it to a `const`/`static const`. The `()` at the end calls it right away.
- **`static` local variable for one-time init** — a `static` local is initialized exactly once on first call and lives for the program's lifetime. Used for runtime singletons (e.g. `static const auto path = computePath();`).

- **`std::ios` and stream mode flags** — `std::ios` is a base class that holds constants for controlling how file streams open: `app` (append), `in` (read), `out` (write), `trunc` (truncate). Used as `std::ios::app` etc.
- **`std::ofstream` / `std::ifstream`** — output/input file streams from `<fstream>`. Open on construction, close on destruction (RAII). `<<` to write, `std::getline` to read line by line. Check success with `if (f)`.

- **Move assignment operator** (`operator=(T&&)`) — solid on the move *constructor*,
  but the assignment version (release my own resource first, *then* steal) was only
  touched lightly.
- **Ref-qualified member functions** (`foo() &` / `&&` / `const&`) — e.g. the
  `operator*` overloads in `stdx::Result`. Move semantics are solid now, but I
  haven't decoded these method-level qualifiers yet. ← next rung.
- **Virtual destructors / the vtable** — can use `virtual`, but the underlying
  vtable / vptr / dynamic-dispatch mechanism is fuzzy.
- **Unions / type punning** — know the syntax, hazy on the "only one member is
  live at a time" model and why it matters.

## Not yet covered (teach before using)

Anything past ~move semantics, and the library-author tier in general:
perfect forwarding / `std::forward`, variadic templates (`Args&&...`),
`noexcept` specifications, SFINAE / `std::enable_if`, type traits as used in
conditions, template specialization, placement-new (`::new (ptr) T(...)`),
manual special-member writing, concepts/`requires`, ranges.

## Platform-neutral systems foundations — background (not yet covered, teach before using)

I came to C++ via LeetCode (single-file, compile-and-run), so the portable layer
*under* the language — how a program talks to an OS and what a toolchain produces
— is new. None of the following are known yet; teach each before relying on it:

- **The OS / hardware boundary** — that a program can't touch hardware itself and
  must *ask the OS* to draw, read files, allocate, etc.
- **"Native" binary** — code that calls the OS directly, with no translation layer.
- **Static vs dynamic linking** — whether dependency code is copied into the
  program or resolved from a shared library at load/runtime.
- **API vs ABI** — the source-level contract versus the compiled, machine-level
  calling and data-layout contract.
- **Name mangling / `extern "C"`** — C++ encodes argument types into symbol
  names; `extern "C"` opts a symbol out so C code can link to it.

The `windows-standards:windows-cpp-knowledge` and `gpp-standards:gpp-toolchain` skills own the
platform/toolchain-specific calibration that layers on these foundations.
