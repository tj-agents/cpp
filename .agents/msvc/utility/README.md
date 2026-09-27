# MSVC utilities

`msvc:scaffold` owns the reusable user-mode console project scaffold. Its runtime scripts and MSVC templates live in `scripts/`; the shared templates it layers underneath belong to `base/utility/scripts/templates/`.

`scripts/Install-ClangdMsvc.ps1` is per-machine editor setup owned by `msvc:toolchain`, never copied into projects. It installs `scripts/clangd-msvc.cmd`, a clangd launcher that enters the MSVC developer environment, and points the VS Code user settings at it.
