import json
import os
import subprocess
import sys
from pathlib import Path


CPP_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ixx"}
CPP_FILES = {"CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy"}
ROUTES_FILE = Path(".agents") / "skill-routes.json"
KIND_ALIASES = {"portable": "generic", "gpp": "gcc"}
PROJECT_KINDS = {"generic", "gcc", "windows", *KIND_ALIASES}
PROJECT_LAYERS = {"base", "gcc", "windows"}
WINDOWS_MARKERS = (
    "#include <windows.h>",
    "#include <wil/",
    "winmain(",
    "wwinmain(",
    "createwindowex",
    "defwindowproc",
)
LEGACY_PLUGIN_NAME = "cpp-standards"


def context_messages(plugin_name: str) -> tuple[str, str, str]:
    if plugin_name == LEGACY_PLUGIN_NAME:
        return (
            "This is a C++ repository. Apply cpp-standards@cpp-agents. Load cpp-standards:cpp-style and cpp-standards:cpp-libraries before code changes, and cpp-standards:cpp-learning plus cpp-standards:cpp-knowledge before deciding how to teach or implement unfamiliar logic.",
            "Native Windows C++ was detected. Apply windows-standards@windows-agents on top of cpp-standards: windows-standards:windows-overview, windows-standards:win32-style, and windows-standards:windows-cpp-knowledge.",
            "GCC/Linux C++ applies to this repository. Apply gpp-standards@cpp-agents and gpp-standards:gpp-toolchain on top of cpp-standards.",
        )
    return (
        "This is a C++ repository. Apply base@cpp-agents. Load base:cpp-style and base:cpp-libraries before code changes, and base:cpp-learning plus base:cpp-knowledge before deciding how to teach or implement unfamiliar logic.",
        "Native Windows C++ was detected. Apply windows@cpp-agents on top of base: windows:windows-overview, windows:win32-style, and windows:windows-cpp-knowledge.",
        "GCC/Linux C++ applies to this repository. Apply gcc@cpp-agents and gcc:gcc-toolchain on top of base.",
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


def declared_layers(root: Path) -> frozenset[str] | None:
    try:
        routes = json.loads((root / ROUTES_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(routes, dict):
        return None
    layers = routes.get("layers")
    if (
        isinstance(layers, list)
        and layers
        and all(isinstance(layer, str) for layer in layers)
        and set(layers) <= PROJECT_LAYERS
        and "base" in layers
    ):
        return frozenset(layers)
    value = routes.get("kind")
    if value not in PROJECT_KINDS:
        return None
    kind = KIND_ALIASES.get(value, value)
    return frozenset({"base"} if kind == "generic" else {"base", kind})


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


def context_for(
    cwd: Path,
    platform: str = sys.platform,
    plugin_name: str | None = None,
) -> list[str]:
    root, files = tracked_project(cwd)
    layers = declared_layers(root)
    if not is_cpp_project(files) and layers is None:
        return []

    if layers is None:
        layers = {"base"}
        if is_native_windows(root, files):
            layers.add("windows")
        elif platform.startswith("linux"):
            layers.add("gcc")

    base_message, windows_message, gcc_message = context_messages(
        plugin_name or Path(__file__).resolve().parents[1].name
    )
    context = [base_message]
    if "windows" in layers:
        context.append(windows_message)
    if "gcc" in layers:
        context.append(gcc_message)
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
