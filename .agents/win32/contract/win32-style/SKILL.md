---
name: win32-style
description: Native Win32 C++ design rules covering Unicode, MSVC, WIL, RAII handles, callbacks, object lifetimes, errors, and thin OS glue.
kind: contract
domain: cpp
---

# Code conventions — Win32 / Windows C++ (Tommy)

Idiomatic modern C++ wrapping an old C API. It layers on `cpp:cpp-style`
(trailing-underscore members, `{}` init, snake_case / PascalCase); this file adds only
the Win32-specific rules. Each is tagged **[platform]** (the OS punishes you if you
break it — not negotiable) or **[style]** (house taste, but hold it).

## Library stack — WIL is the default

| Library | For | Verdict |
|---|---|---|
| **WIL** (`microsoft/wil`) | RAII handles (`unique_handle`, `unique_hfile`, `unique_hmenu`…), `wil::com_ptr`, error macros | **Default** for classic Win32/COM. Header-only |
| **C++/WinRT** | Windows Runtime APIs (`winrt::com_ptr`) | Use for WinRT |
| **WRL `ComPtr`** | — | Legacy only; never start new code on it |

WIL doesn't violate the std-first rule: it covers Win32/COM resources `std::` has no
equivalent for. *Learning carve-out:* hand-roll **one** RAII handle wrapper, once, to
meet the mechanism (`= delete` copy, move-only, the sentinel problem below) — then use
WIL's.

## Header hygiene — [platform]

```cpp
#define WIN32_LEAN_AND_MEAN   // drop rarely-used sub-headers (winsock, RPC, shell, …)
#define NOMINMAX              // stop windows.h #define-ing min/max as macros
#include <windows.h>
```

- **`NOMINMAX` is not optional** — the `min`/`max` macros silently break `std::min` /
  `std::max` / `std::numeric_limits<>::max()`.
- **`<windows.h>` before every other Windows header** (`<commctrl.h>`, `<shellapi.h>`):
  they *use* macros it *defines* (`CALLBACK`) and don't include it themselves. Get it
  backwards → `error C2065: 'CALLBACK'` in `prsht.h` and a cascade. clang-format's
  `SortIncludes` alphabetizes and silently swaps them — pin `<windows.h>` to Priority 1
  via `IncludeCategories`.
- `UNICODE` / `_UNICODE` are defined project-wide in CMake, not per-file (API and CRT
  respectively — define both).

## Unicode & strings — [platform]

Windows is UTF-16 internally. Don't fight it; convert at the edges.

1. **Always the `…W` functions** and wide types: `wWinMain`, `wchar_t` / `L"…"`,
   `std::wstring`, `WNDCLASSW`. Never `…A`.
2. **`std::wstring` = UTF-16** (the Win32 boundary); **`std::string` = UTF-8**
   (everything else — my code, files, the network).
3. **Convert only at the boundary**: `MultiByteToWideChar` / `WideCharToMultiByte`, or
   WIL's `wil::str_*`.
4. **`/utf-8`** so narrow literals are UTF-8 in the binary (separate from the runtime
   active code page — see §Manifest).
5. **No `TCHAR` / `_T("…")`** — that layer is for ANSI/Unicode dual builds we never do.

## Handles & cleanup

- **[platform]** Never call `CloseHandle` / `DestroyWindow` / `RegCloseKey` /
  `DeleteObject` by hand in the normal path — every raw handle gets a RAII owner (a WIL
  `unique_*`, or a small move-only owner). No `goto Cleanup;` ladders.
- **[platform]** **Sentinel gotcha:** "invalid" isn't one value. `CreateFile` returns
  `INVALID_HANDLE_VALUE` (`-1`); most other `Create*`/`Open*` return `nullptr`. Hence
  the distinct WIL types.
- **[style]** One owner per resource; pass borrows as the raw handle (non-owning view,
  same spirit as `string_view`).
- **[style]** *Exception:* when teardown needs a specific **sequence** (the
  detach-then-`DestroyWindow` below), a deliberate destructor beats an RAII member —
  be explicit about ordering rather than hiding it.

## Errors — translate at the boundary

Raw `BOOL` / `HRESULT` never leak inward.

- **Library APIs:** `std::expected<T, std::error_code>`, built from
  `std::system_category()` (which understands Win32 codes):

  ```cpp
  std::error_code ec{static_cast<int>(::GetLastError()), std::system_category()};
  ```

- **App code:** WIL's exceptions mode — `THROW_IF_WIN32_BOOL_FALSE(::SomeApi(...))`,
  `THROW_IF_FAILED(obj->Method(...))`. `RETURN_IF_*` only where code must stay
  exception-free; `FAIL_FAST_IF_*` for invariant breaks.

## Wrap the ceremony once — [style]

- Class registration, window creation and callback routing go in a **class template**
  `Window<T>` once, not per window. If every window does X, X lives in the base.
- **No `virtual`.** The derived type defines its own `handle_message`, resolved at
  compile time — historically CRTP + `static_cast<T*>`; winwrap now respells it as
  C++23 *deducing this* plus composed mixins (see `winwrap/MIXINS.md`). Not MSVC's
  `__super::` — keep it portable.

## Object lifetime — any object that hands `this` to the OS — [platform]

The difference between "compiles" and "correct".

- **Build the object fully, *then* create the window — static factory, not a
  constructor.** `CreateWindowEx` dispatches `WM_NCCREATE` / `WM_CREATE` *synchronously
  before it returns*, so those messages would reach half-initialised members. A
  `create(...)` factory constructs the object (private ctor, no window), then
  `CreateWindowExW(..., this)`, returning `std::unique_ptr<T>` — and can report failure
  where a constructor can't.
- **`= delete` copy *and* move.** The object's address is stored in the OS
  (`SetWindowLongPtr(GWLP_USERDATA, this)`); relocating it hands the callback a stale
  pointer.
- **Detach before you destroy.** `~Derived` runs before `~Base`, and `DestroyWindow`
  sends `WM_DESTROY` / `WM_NCDESTROY` synchronously — null the `GWLP_USERDATA` slot
  *first*.

## The C-callback → C++-object bridge — [platform]

The window procedure **must** be `static` (or free). Bridge it: pass `this` as the last
`CreateWindowEx` argument, recover it in `WM_NCCREATE` from
`CREATESTRUCT::lpCreateParams`, stash it via `SetWindowLongPtr(GWLP_USERDATA)`, read it
back on later messages, dispatch to the member handler. Guard `self == nullptr` →
`DefWindowProc`: a few messages (`WM_GETMINMAXINFO`) arrive *before* `WM_NCCREATE`.
*This is the heart of a Win32 app — Tommy writes it himself.*

When **subclassing an existing control** (one Windows made), don't use `GWLP_USERDATA`
— it may already be in use — use `SetWindowSubclass` / `SetProp`. The heavier classic
alternatives (VCL's dynamic thunk, MFC's CBT hook, an `unordered_map<HWND, Window*>`)
aren't worth it for windows you create.

## Separation — [style]

- The **message loop is per-thread, not per-window** — it lives in `wWinMain`. One loop
  drives every window.
- Keep the Win32 layer thin: the handler only dispatches; real logic lives in plain
  platform-agnostic classes, unit-testable with **Catch2** without a message pump.
- File-local helpers and message / ID constants go in an anonymous `namespace { }`.

## HINSTANCE — fetch it, don't thread it

- **[style]** Get it inside the `Window` base via `GetModuleHandle(nullptr)`, stored
  once as a `const` member, instead of threading `wWinMain`'s `HINSTANCE` through every
  constructor.
- **[platform]** It returns the **exe's** handle — wrong for a DLL, which must use its
  own from `DllMain`.

## Manifest — the standard four settings

MSVC auto-embeds a default; customize by adding a `.manifest` to the target's sources.
Baseline: **DPI awareness** `Per-Monitor v2` (via the manifest, not
`SetProcessDpiAwarenessContext`), **Common Controls v6** (`<dependency>` on
`Microsoft.Windows.Common-Controls` 6.0 — themed, not Win95-grey), **`activeCodePage =
UTF-8`** (Win10 1903+), **`requestedExecutionLevel = asInvoker`** (don't silently ask
for admin).

## Build (CMake + MSVC or clang-cl)

- Generic compiler, SDK, runtime, build-system and editor configuration lives in
  `msvc:msvc-toolchain`. The following settings apply specifically to Win32 app targets.
- `add_executable(app WIN32 …)` → GUI subsystem (`WinMain`, no console); omit `WIN32`
  for a console app (`main`).
- `target_compile_definitions(app PRIVATE UNICODE _UNICODE)`;
- MSVC auto-links many system libs via `#pragma comment(lib, …)`; link the rest
  (`comctl32`, `ole32`, …) explicitly.
- WIL via `FetchContent` (`GIT_SHALLOW`, `SYSTEM`, `WIL_BUILD_TESTS`/`_PACKAGING` OFF),
  exposing `WIL::WIL`.

## References

The good, authoritative Win32 sources (most guidance online is scattered and 20 years old):

- Raymond Chen — *Saving the window handle too late* (the `WM_NCCREATE` rule):
  https://devblogs.microsoft.com/oldnewthing/20191014-00/?p=102992
- Raymond Chen — *Making a WNDPROC a member of your C++ class*:
  https://devblogs.microsoft.com/oldnewthing/20140203-00/?p=1893
- Kenny Kerr — *Classy Windows*: https://kennykerrca.wordpress.com/2014/03/29/classy-windows-2/
- ENLYZE — *Writing Win32 apps like it's 2020*:
  https://building.enlyze.com/posts/writing-win32-apps-like-its-2020-part-2/
