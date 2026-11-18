---
name: overview
description: Orientation for Tommy's user-mode Win32 C++ tier including Unicode, WIL, project scope, and independent toolchain selection.
kind: reference
domain: cpp
profile: knowledge
applicability: Projects explicitly selecting win32
requires: cpp
provenance: house
---

# Windows / Win32 API tier

This tier covers user-mode native Windows APIs. It owns Win32, Unicode boundaries,
Windows resources, callbacks, handles, and supported helper libraries. It does not choose
a compiler. A consuming repository selects `gpp` or `msvc` separately when it needs one.

Load `cpp` first, then [the Win32 learner record](../../learning/knowledge.md) for calibration and
`win32:style` when writing Windows API glue. Language-version defaults remain in
`cpp`. If the repository selects MSVC/clang-cl, also load `msvc:toolchain`; if it
selects G++, load `gpp:toolchain` instead.

`cpp:learning` owns teaching and progress; the Win32 learner record contains the current calibration.

## Projects

**`winwrap`** — the library these conventions were shaped around; it has its own
project guidance. `icon-dropper` is a small app. `wifi-toggle` is legacy:
ANSI strings and `virtual` dispatch, pre-dates these rules; don't copy its style.

## Example

```text
Selection: a Win32 API application built with G++.
Guidance: cpp + gpp + win32.
Compiler and debugger: selected by gpp, independently of the Win32 API.
```
