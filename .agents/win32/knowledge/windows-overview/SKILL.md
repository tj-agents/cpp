---
name: windows-overview
description: Orientation for Tommy's user-mode Win32 C++ tier including Unicode, WIL, project scope, and independent toolchain selection.
kind: knowledge
domain: cpp
---

# Windows / Win32 API tier

This tier covers user-mode native Windows APIs. It owns Win32, Unicode boundaries,
Windows resources, callbacks, handles, and supported helper libraries. It does not choose
a compiler. A consuming repository selects `gpp` or `msvc` separately when it needs one.

Load `cpp` first, then `win32:windows-cpp-knowledge` for calibration and
`win32:win32-style` when writing Windows API glue. Language-version defaults remain in
`cpp`. If the repository selects MSVC/clang-cl, also load `msvc:msvc-toolchain`; if it
selects G++, load `gpp:gpp-toolchain` instead.

> **Calibration:** I have *not* learned Win32 — `win32:windows-cpp-knowledge` is at
> ground zero. Teach each concept in chat before relying on it, and never promote a
> concept merely because it was explained.

## Projects

**`winwrap`** — the library these conventions were shaped around; it has its own
project guidance. `icon-dropper` is a small app. `wifi-toggle` is legacy:
ANSI strings and `virtual` dispatch, pre-dates these rules; don't copy its style.
