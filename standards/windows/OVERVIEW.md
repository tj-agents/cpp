# Windows / Win32 — the MSVC tier

This tier covers **MSVC/clang-cl C++ toolchains and native Windows APIs**.
[MSVC.md](MSVC.md) is the generic toolchain standard for applications and libraries,
including console and portable-library projects with no Win32 boundary. It does not
require WIL, a GUI, one architecture, or one Visual Studio version.

Load the shared `base` plugin first and this tier's [KNOWLEDGE.md](KNOWLEDGE.md)
calibration. Use [WIN32.md](WIN32.md) when writing Windows API glue; that boundary
adds Unicode and WIL resource conventions. Language-version defaults remain in base.

> **Calibration:** I have *not* learned Win32 — `KNOWLEDGE.md` is at ground
> zero. Teach each concept in chat before relying on it, and never promote anything
> from these docs into a `WHAT_I_KNOW`: they're the style we're *aiming* at, not what
> I know.

Compiler and editor-diagnostic guidance lives in [MSVC.md](MSVC.md).

## Projects

**`winwrap`** — the library these conventions were shaped around; it has its own
project guidance. `icon-dropper` is a small app. `wifi-toggle` is legacy:
ANSI strings and `virtual` dispatch, pre-dates these rules; don't copy its style.
