import json
import os
import subprocess
import sys
from pathlib import Path


CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ixx"}
CPP_FILES = {"CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy"}
ROUTES_FILE = Path(".agents") / "skill-routes.json"
PROJECT_KINDS = {"portable", "gpp", "windows"}
WINDOWS_MARKERS = (
    "#include <windows.h>",
    "#include <wil/",
    "winmain(",
    "wwinmain(",
    "createwindowex",
    "defwindowproc",
)


def project_root(cwd: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / ROUTES_FILE).is_file():
            return candidate
    return cwd


def tracked_project(cwd: Path) -> tuple[Path, list[str]]:
    root = project_root(cwd)
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode == 0:
        return root, [line for line in result.stdout.splitlines() if line]
    return root, [item.name for item in root.iterdir() if item.is_file()]


def declared_kind(root: Path) -> str | None:
    try:
        routes = json.loads((root / ROUTES_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(routes, dict):
        return None
    value = routes.get("kind")
    return value if value in PROJECT_KINDS else None


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


def context_for(cwd: Path, platform: str = sys.platform) -> list[str]:
    root, files = tracked_project(cwd)
    kind = declared_kind(root)
    if not is_cpp_project(files) and kind is None:
        return []

    context = [
        "This is a C++ repository. Apply the installed cpp-standards base. Load cpp-style and cpp-libraries before code changes, and cpp-learning plus cpp-knowledge before deciding how to teach or implement unfamiliar logic."
    ]
    if kind == "windows" or (kind is None and is_native_windows(root, files)):
        context.append("Native Windows C++ was detected. Apply windows-standards:windows-overview, windows-standards:win32-style, and windows-standards:windows-cpp-knowledge on top of the generic C++ base.")
    elif kind == "gpp" or (kind is None and platform.startswith("linux")):
        context.append("GNU/Linux C++ applies to this repository. Apply gpp-standards:gpp-toolchain on top of the generic C++ base.")
    return context


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, TypeError):
        payload = {}
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    context = context_for(cwd)
    if not context:
        return
    print("\n".join(context))


if __name__ == "__main__":
    main()
