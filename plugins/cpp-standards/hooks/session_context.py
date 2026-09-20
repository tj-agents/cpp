import json
import os
import subprocess
import sys
from pathlib import Path


CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ixx"}
CPP_FILES = {"CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy"}
ROUTES_FILE = Path(".agents") / "skill-routes.json"
WINDOWS_MARKERS = ("#include <windows.h>", "#include <wil/", "winmain(", "wwinmain(", "createwindowex", "defwindowproc")
CPP_CONTEXT = "This is a C++ repository. Apply cpp-standards@cpp-agents. Load cpp-standards:cpp-style and cpp-standards:cpp-libraries before code changes, and cpp-standards:cpp-learning plus cpp-standards:cpp-knowledge before teaching or implementing unfamiliar logic."
GPP_CONTEXT = "The repository explicitly selects G++. Apply gpp-standards@cpp-agents and gpp-standards:gpp-toolchain on top of cpp."
MSVC_CONTEXT = "The repository explicitly selects MSVC/clang-cl. Apply windows@cpp-agents and windows:msvc-toolchain on top of cpp. This does not select Win32 APIs."
WIN32_CONTEXT = "The repository explicitly selects user-mode Win32 APIs. Apply windows@cpp-agents, windows:windows-overview, windows:win32-style, and windows:windows-cpp-knowledge. The compiler is selected separately."
WIN32_SUGGESTION = "Win32 source markers were detected, but no API profile is declared. Consider selecting win32 explicitly; detection does not apply it or choose MSVC."


def project_root(cwd: Path) -> Path:
    result = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / ROUTES_FILE).is_file():
            return candidate
    return cwd


def tracked_project(cwd: Path) -> tuple[Path, list[str]]:
    root = project_root(cwd)
    result = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode == 0:
        return root, [line for line in result.stdout.splitlines() if line]
    return root, [item.name for item in root.iterdir() if item.is_file()]


def declared_profile(root: Path) -> tuple[str | None, frozenset[str]] | None:
    try:
        declaration = json.loads((root / ROUTES_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(declaration, dict):
        return None
    profile = declaration.get("profile")
    if isinstance(profile, dict):
        toolchain = profile.get("toolchain")
        apis = profile.get("apis", [])
        if toolchain in (None, "gpp", "msvc") and isinstance(apis, list) and set(apis) <= {"win32"}:
            return toolchain, frozenset(apis)
        return None
    kind = declaration.get("kind")
    if kind in ("generic", "portable"):
        return None, frozenset()
    if kind in ("gcc", "gpp"):
        return "gpp", frozenset()
    if kind == "windows":
        return "msvc", frozenset({"win32"})
    layers = declaration.get("layers")
    if isinstance(layers, list):
        values = set(layers)
        if values <= {"base", "cpp", "gcc", "gpp", "windows", "msvc", "win32"}:
            toolchain = "gpp" if values & {"gcc", "gpp"} else ("msvc" if values & {"windows", "msvc"} else None)
            apis = frozenset({"win32"}) if values & {"windows", "win32"} else frozenset()
            return toolchain, apis
    return None


def is_cpp_project(files: list[str]) -> bool:
    return any(Path(file).suffix.lower() in CPP_SUFFIXES or Path(file).name in CPP_FILES for file in files)


def is_native_windows(cwd: Path, files: list[str]) -> bool:
    if any(Path(file).suffix.lower() in {".manifest", ".rc"} for file in files):
        return True
    command = ["git", "-C", str(cwd), "grep", "--quiet", "-I", "-i", "-F"]
    for marker in WINDOWS_MARKERS:
        command.extend(["-e", marker])
    command.extend(["--", *(f":(icase)*{suffix}" for suffix in sorted(CPP_SUFFIXES))])
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode in {0, 1}:
        return result.returncode == 0
    for relative in (file for file in files if Path(file).suffix.lower() in CPP_SUFFIXES):
        try:
            with (cwd / relative).open(encoding="utf-8", errors="ignore") as source:
                for line in source:
                    lowered = line.lower()
                    if any(marker in lowered for marker in WINDOWS_MARKERS):
                        return True
        except OSError:
            continue
    return False


def context_for(cwd: Path, platform: str = sys.platform) -> list[str]:
    del platform
    root, files = tracked_project(cwd)
    profile = declared_profile(root)
    if not is_cpp_project(files) and profile is None:
        return []
    context = [CPP_CONTEXT]
    if profile is None:
        if is_native_windows(root, files):
            context.append(WIN32_SUGGESTION)
        return context
    toolchain, apis = profile
    if toolchain == "gpp":
        context.append(GPP_CONTEXT)
    elif toolchain == "msvc":
        context.append(MSVC_CONTEXT)
    if "win32" in apis:
        context.append(WIN32_CONTEXT)
    return context


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, TypeError):
        payload = {}
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    context = context_for(cwd)
    if context:
        print("\n".join(context))


if __name__ == "__main__":
    main()
