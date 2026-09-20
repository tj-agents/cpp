---
name: windows-cpp-knowledge
description: Tommy's current proven Windows and Win32 knowledge used to identify concepts that must be taught before use.
kind: knowledge
domain: cpp
---

# What I know — Windows / Win32 (Tommy)

Companion to `cpp:cpp-knowledge`, but for the Windows-native layer: the
Win32 API, Windows executable model, COM, and everything in that world. Toolchain
knowledge is recorded here only where it intersects the platform boundary. Same purpose — so anyone (me or Claude) can calibrate to my level. Same
rule: **nothing moves into "comfortable" until I've *proven* it** (written it or
explained it back), not just had it explained to me. I'm the sole judge.

Legend: 🟡 = seen it but shaky.

> **Status: ground zero.** I came to C++ via LeetCode (single-file,
> compile-and-run), so almost the entire Windows layer is new. Right now
> essentially everything below is "not yet covered." Teach each item before
> relying on it.

## Comfortable with

- (nothing yet — this fills in as I go)

## Seen but shaky 🟡

- (nothing yet)

## Not yet covered (teach before using)

Rough learning order. None of this is known yet.

**The platform model**
- OS / hardware boundary — a program can't touch hardware; it *asks the OS*.
- Win32 API — the C function surface Windows exposes for those requests.
- System DLLs — `kernel32` / `user32` / `gdi32` / `shell32` (always present).
- "Native" binary — calls the OS directly, no translation layer.
- PE (Portable Executable) — the Windows `.exe` / `.dll` file format.
- Static vs dynamic linking; import libraries (a `.lib` that resolves to a DLL).

**Toolchain & build** *(selected independently from the Win32 API)*
- MSVC (`cl.exe`), clang-cl, and MinGW/G++ are distinct compiler and ABI choices.
- The project profile selects `msvc` or `gpp`; the Windows host and Win32 API do not.
- ABI — the machine-level calling contract and why libraries must match the selected
  compiler, runtime, architecture, and calling convention.
- Name mangling / `extern "C"` — opting a symbol out of C++ mangling.
- Subsystem: console (`main`) vs GUI (`WinMain`); CMake's `WIN32` target option.
- The `UNICODE` / `_UNICODE` defines; embedding the app manifest (DPI, Common
  Controls v6, UTF-8 code page) through the selected toolchain.
- Linking Windows import libraries (`user32`, `gdi32`, …) explicitly in the build model.

**Handles & objects**
- `HANDLE` / `HWND` / `HKEY` / `HDC` and friends — opaque OS resource handles.
- The two "invalid" sentinels: `nullptr` vs `INVALID_HANDLE_VALUE`.
- Cleanup funcs (`CloseHandle` / `DestroyWindow` / `RegCloseKey` / `DeleteObject`)
  and why each handle type needs its own RAII wrapper.
- Kernel vs USER vs GDI objects (different lifetimes / limits).

**Strings & Unicode**
- UTF-16 / `wchar_t` / `std::wstring` as the native encoding.
- `…W` vs `…A` functions; why new code is always `…W`.
- `TCHAR` / `_T()` (legacy dual-build macro layer) — and why we skip it.
- `MultiByteToWideChar` / `WideCharToMultiByte` boundary conversions.
- `BSTR`, `LPWSTR`, `LPCWSTR` and the rest of the Hungarian type zoo.

**Errors**
- `GetLastError()` + the `BOOL`-returning convention.
- `HRESULT`, `SUCCEEDED` / `FAILED` — the COM convention.
- `FormatMessage` to turn a code into text.
- `std::system_error` / `std::error_code` / `std::system_category()` — the
  std-native carrier.

**Processes, threads, synchronization**
- `CreateProcess`; `CreateThread` vs `_beginthreadex` (why the CRT one).
- `WaitForSingleObject` / `WaitForMultipleObjects`; waitable handles.
- Events, mutexes, semaphores, critical sections; `SRWLOCK`.

**GUI & the message model**
- `WinMain` / `wWinMain` entry point.
- Window class registration (`WNDCLASSEX`, `RegisterClassEx`).
- `CreateWindowEx`; the message loop (`GetMessage` / `TranslateMessage` /
  `DispatchMessage`); `WndProc` and `WM_*` messages.
- The static-`WndProc` → C++-object idiom (`lpCreateParams` + `WM_NCCREATE` +
  `SetWindowLongPtr(GWLP_USERDATA)`).
- Why it's an event/message model, not a call-stack one.

**Graphics (aspirational)**
- GDI (`HDC`, `BeginPaint`, `WM_PAINT`), GDI+, Direct2D / DirectX.

**Filesystem, registry, shell**
- Win32 file APIs vs `std::filesystem`; when each is needed.
- Registry (`RegOpenKeyEx` …); the shell APIs.

**COM (later)**
- `CoInitializeEx` (+ RAII); apartments (STA / MTA).
- `IUnknown`, `AddRef` / `Release` / `QueryInterface`; ref-counting.
- COM smart pointers: hand-rolled, or `wil::com_ptr` / `winrt::com_ptr` on MSVC.

**WinRT (much later)**
- The modern projection (C++/WinRT) over the newer Windows Runtime APIs.

## See also
- `win32:windows-overview` — the tier's orientation; `win32:win32-style` is the
  full Win32 house style.
- `cpp:cpp-knowledge` — the general C++ level this file extends.
