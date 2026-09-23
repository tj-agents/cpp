---
name: scaffold
description: Convert a freshly generated G++ or MSVC console scaffold into a user-mode Win32 GUI application with wWinMain, an embedded application manifest, and Win32 analysis settings, without choosing the compiler.
kind: utility
domain: cpp
---

# Win32 application scaffold

This is an overlay, not a project generator. Create the project first with the selected
toolchain's scaffold — `gpp:scaffold` or `msvc:scaffold` — then convert its `app` target.
Selecting Win32 never selects a compiler, and the result keeps the toolchain's presets,
warnings, sanitizer carrier and build helpers. Use `win32:style` for the design rules this
starter follows.

## Convert a project

Run the bundled [Add-Win32App.ps1](../scripts/Add-Win32App.ps1) from PowerShell 7. Resolve
its path relative to this document, including when using an installed plugin:

```powershell
& <skill-directory>/../scripts/Add-Win32App.ps1 -Project C:/source/my_tool
```

`-WhatIf` previews the conversion. The script refuses to run unless `app/CMakeLists.txt`
and `app/src/main.cpp` are still the unmodified scaffold output and no `app.manifest` or
`app.rc` exists, so it never overwrites application code. It changes only:

- `app/src/main.cpp` — a `wWinMain` entry point with no console window;
- `app/CMakeLists.txt` — `WIN32` executable, `UNICODE`/`_UNICODE`/`WIN32_LEAN_AND_MEAN`/
  `NOMINMAX`, the Win32 import libraries, `/MANIFEST:NO` for MSVC-style linkers and
  `-municode` for GNU-style drivers;
- `app/app.manifest` and `app/app.rc` — Per-Monitor V2 DPI awareness, Common Controls v6,
  UTF-8 active code page and `asInvoker`, embedded as a resource so MSVC and MinGW builds
  carry the same manifest;
- `.clang-tidy` — the Win32 carve-outs (reinterpret casts and int-to-pointer conversions,
  instance message hooks, unnamed callback parameters), and `.clang-format` — `<windows.h>`
  pinned to the first include block. A configuration that differs from the canonical one is
  left untouched and reported as a manual step;
- `AGENTS.md` and `README.md` — the project facts; and `.agents/skill-routes.json`, when the
  package ships route profiles and the file is still the unmodified console profile, becomes
  the same toolchain's profile with the Win32 API selected. A customized route profile is
  left untouched and reported as a manual step.

Build exactly as before — `./scripts/Build.ps1 -Test` for MSVC, `cmake --preset …` for
G++. A MinGW toolchain has no sanitizer runtimes, so use its `gdb` preset.

## Validation and publication

Convert fresh MSVC and G++ scaffolds, build and run each with the real compiler, confirm
the manifest is embedded, and exercise refusal on a modified `app`. Legacy
`windows@cpp-agents` carries this overlay without route profiles.

The skill, script and templates are authored once under `.agents/win32/utility/` and copied
to plugin payloads by `sync-generated.ps1`; the shared application templates it verifies
against belong to `.agents/base/utility/scripts/`. Never edit the generated copies.
