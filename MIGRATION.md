# Current C++ selection

Select platform-neutral `cpp`, then independently select `gpp` or `msvc` for a compiler and `win32`
when using the Windows API. No compiler is inferred from the operating system or API selection.

Generate the explicit route profile with the shipped entry point:

```powershell
python -B .agents/gen_skill_routes.py --toolchain msvc --api win32 --into C:/repos/my-app
python -B .agents/gen_skill_routes.py --toolchain gpp --into C:/repos/my-library
```

The declaration uses `profile: {toolchain, apis}`. Check it with the same command plus `--check`.
Packages expose current names such as `cpp:style`, `gpp:toolchain`, `msvc:scaffold` and `win32:style`.
Flat host discovery names are generated scope-qualified adapters to these same authored definitions.
Retired combined packages, forwarding skills and route options are no longer accepted.
