import json
import os
import subprocess
import sys
from pathlib import Path


CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ixx"}
CPP_FILES = {"CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy"}
WINDOWS_MARKERS = ("#include <windows.h>", "#include <wil/", "winmain(", "wwinmain(", "createwindowex", "defwindowproc")
CPP_CONTEXT = "This is a C++ repository. Apply cpp@tj-agents. Load cpp:style and cpp:libraries before code changes, cpp:domain-design when designing records, invariants, operations, or component boundaries, and cpp:learning plus cpp:knowledge before teaching or implementing unfamiliar logic."
WIN32_SUGGESTION = "Win32 source markers were detected. Consider selecting win32 explicitly; detection does not apply it or choose MSVC."


def project_root(cwd: Path) -> Path:
    result = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return cwd


def tracked_project(cwd: Path) -> tuple[Path, list[str]]:
    root = project_root(cwd)
    result = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode == 0:
        return root, [line for line in result.stdout.splitlines() if line]
    return root, [item.name for item in root.iterdir() if item.is_file()]


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
    if not is_cpp_project(files):
        return []
    context = [CPP_CONTEXT]
    if is_native_windows(root, files):
        context.append(WIN32_SUGGESTION)
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
