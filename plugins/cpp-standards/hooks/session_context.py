import json
import os
import subprocess
import sys
from pathlib import Path


CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ixx"}
CPP_FILES = {"CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy"}
WINDOWS_MARKERS = (
    "#include <windows.h>",
    "#include <wil/",
    "winmain(",
    "wwinmain(",
    "createwindowex",
    "defwindowproc",
)


def tracked_files(cwd: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(cwd), "ls-files"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode == 0:
        return [line for line in result.stdout.splitlines() if line]
    return [item.name for item in cwd.iterdir() if item.is_file()]


def is_cpp_project(files: list[str]) -> bool:
    return any(Path(file).suffix.lower() in CPP_SUFFIXES or Path(file).name in CPP_FILES for file in files)


def is_native_windows(cwd: Path, files: list[str]) -> bool:
    if any(Path(file).suffix.lower() in {".manifest", ".rc"} for file in files):
        return True
    candidates = [file for file in files if Path(file).suffix.lower() in CPP_SUFFIXES]
    for relative in candidates[:200]:
        try:
            text = (cwd / relative).read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(marker in text for marker in WINDOWS_MARKERS):
            return True
    return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, TypeError):
        payload = {}
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    files = tracked_files(cwd)
    if not is_cpp_project(files):
        return

    context = [
        "This is a C++ repository. Apply the installed cpp-standards base. Load cpp-style and cpp-libraries before code changes, and cpp-learning plus cpp-knowledge before deciding how to teach or implement unfamiliar logic."
    ]
    if is_native_windows(cwd, files):
        context.append("Native Windows C++ was detected. Apply windows-standards:windows-overview, windows-standards:win32-style, and windows-standards:windows-cpp-knowledge on top of the generic C++ base.")
    elif sys.platform.startswith("linux"):
        context.append("This is running on Linux. Apply gpp-standards:gpp-toolchain on top of the generic C++ base.")
    print("\n".join(context))


if __name__ == "__main__":
    main()
