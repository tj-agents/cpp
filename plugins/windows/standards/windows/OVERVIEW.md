# Windows / Win32 — the MSVC tier

This tier covers **native Win32 C++ built with MSVC** (Build Tools
for VS; clang-cl is a fine drop-in — never MinGW). WIL, header-only, is the one
sanctioned dependency. C++23, Unicode-only.

Load the shared `base` plugin first, then this tier's
[WIN32.md](WIN32.md) conventions and [KNOWLEDGE.md](KNOWLEDGE.md) calibration.

> **Calibration:** I have *not* learned Win32 — `KNOWLEDGE.md` is at ground
> zero. Teach each concept in chat before relying on it, and never promote anything
> from these docs into a `WHAT_I_KNOW`: they're the style we're *aiming* at, not what
> I know.

Build with MSVC before trusting editor diagnostics — clangd shows phantom
`<expected>` errors here.

## Projects

**`winwrap`** — the library these conventions were shaped around; it has its own
project guidance. `icon-dropper` is a small app. `wifi-toggle` is legacy:
ANSI strings and `virtual` dispatch, pre-dates these rules; don't copy its style.
