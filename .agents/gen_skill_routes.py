#!/usr/bin/env python3
"""Generate independent C++ toolchain and API skill routes."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


CPP_PATH = r"(?i:\.(c|cc|cpp|cxx|h|hh|hpp|hxx|ixx))$"
BUILD_PATH = r"(?i:(^|/)(CMakeLists\.txt|CMakePresets\.json|[^/]+\.cmake))$"
TEST_PATH = r"(?i:(^|/)(tests?|test)/.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx)|(_test|_tests)\.(c|cc|cpp|cxx))$"
WINDOWS_RESOURCE_PATH = r"(?i:\.(rc|manifest))$"
MSVC_BUILD_PATH = r"(?i:\.(vcxproj|props|targets|sln|slnx))$"
TOOLCHAINS = ("gpp", "msvc")
APIS = ("win32",)
LEGACY_KINDS = ("generic", "portable", "gcc", "gpp", "windows")
LEGACY_LAYERS = ("gcc", "windows")
# A route's `skills` block the write until loaded; `conditional` entries are advice the core router names
# with their condition and never demands. Require only what governs every file a route matches.
DOMAIN_DESIGN_WHEN = "designing records, invariant-bearing values, entities, typed errors or stateful boundaries"
MIXINS_WHEN = "composing or changing mixins, CRTP behavior providers or policy-style composition"
STRUCTURE_WHEN = "adding, moving or renaming files, targets or folders, or deciding where code lives"
LIBRARIES_WHEN = "adding, removing or upgrading a dependency (find_package, FetchContent, a backport)"
TOOLCHAIN_WHEN = "using compiler-specific flags, pragmas, intrinsics, warnings or ABI behavior, or diagnosing a build"
WIN32_OVERVIEW_WHEN = "starting Win32 work, or deciding Unicode, WIL or Win32 project scope"


def normalize(toolchain: str | None = None, apis: list[str] | tuple[str, ...] = ()) -> tuple[str | None, tuple[str, ...]]:
    if toolchain not in (None, *TOOLCHAINS):
        raise ValueError(f"unknown toolchain: {toolchain}")
    unknown = set(apis) - set(APIS)
    if unknown:
        raise ValueError(f"unknown API selection(s): {', '.join(sorted(unknown))}")
    return toolchain, tuple(api for api in APIS if api in apis)


def legacy_selection(kind: str | None = None, layers: list[str] | tuple[str, ...] = ()) -> tuple[str | None, tuple[str, ...]]:
    if kind:
        if kind not in LEGACY_KINDS:
            raise ValueError(f"unknown legacy kind: {kind}")
        if kind in ("generic", "portable"):
            return normalize()
        if kind in ("gcc", "gpp"):
            return normalize("gpp")
        return normalize("msvc", ["win32"])
    unknown = set(layers) - set(LEGACY_LAYERS)
    if unknown:
        raise ValueError(f"unknown legacy layer(s): {', '.join(sorted(unknown))}")
    toolchain = "gpp" if "gcc" in layers else ("msvc" if "windows" in layers else None)
    apis = ["win32"] if "windows" in layers else []
    return normalize(toolchain, apis)


def compatibility_kind(toolchain: str | None, apis: tuple[str, ...]) -> str:
    if toolchain is None and not apis:
        return "generic"
    if toolchain == "gpp" and not apis:
        return "gpp"
    if toolchain == "msvc" and apis == ("win32",):
        return "windows"
    return "composed"


def routes(toolchain: str | None = None, apis: list[str] | tuple[str, ...] = ()) -> dict:
    toolchain, apis = normalize(toolchain, apis)
    result = [
        {
            "path": CPP_PATH,
            "skills": ["cpp:style"],
            "conditional": [
                {"skill": "cpp:domain-design", "when": DOMAIN_DESIGN_WHEN},
                {"skill": "cpp:mixins", "when": MIXINS_WHEN},
                {"skill": "cpp:structure", "when": STRUCTURE_WHEN},
            ],
            "note": "C++ style governs every source; design, composition and layout apply when the change does.",
        },
        {
            "path": BUILD_PATH,
            "skills": ["cpp:build", "cpp:structure"],
            "conditional": [{"skill": "cpp:libraries", "when": LIBRARIES_WHEN}],
        },
        {"path": TEST_PATH, "skills": ["cpp:testing"]},
    ]
    if toolchain:
        build_paths = rf"{BUILD_PATH}|{MSVC_BUILD_PATH}" if toolchain == "msvc" else BUILD_PATH
        label = "MSVC/clang-cl" if toolchain == "msvc" else "G++"
        result.append({"path": build_paths, "skills": [f"{toolchain}:toolchain"], "note": f"Explicit {label} toolchain selection."})
        result.append({
            "path": CPP_PATH,
            "conditional": [{"skill": f"{toolchain}:toolchain", "when": TOOLCHAIN_WHEN}],
            "note": f"Explicit {label} toolchain selection; sources need it only for compiler-specific work.",
        })
    if "win32" in apis:
        result.append({
            "path": CPP_PATH,
            "skills": ["win32:style"],
            "conditional": [{"skill": "win32:overview", "when": WIN32_OVERVIEW_WHEN}],
            "note": "Explicit user-mode Win32 API selection; compiler remains independent.",
        })
        result.append({"path": rf"{BUILD_PATH}|{MSVC_BUILD_PATH}|{WINDOWS_RESOURCE_PATH}", "skills": ["win32:overview", "win32:style"], "note": "Explicit user-mode Win32 API selection; compiler remains independent."})
    layers = ["cpp", *([toolchain] if toolchain else []), *apis]
    return {
        "_comment": [
            "Generated by tj-agents/cpp .agents/gen_skill_routes.py; do not edit by hand.",
            "Toolchain and API selections are independent. Host OS never chooses a compiler.",
            "Every matching technical route fires; no process plugin is required.",
        ],
        "kind": compatibility_kind(toolchain, apis),
        "profile": {"toolchain": toolchain, "apis": list(apis)},
        "layers": layers,
        "routes": result,
    }


def routes_from_legacy(kind: str | None = None, layers: list[str] | tuple[str, ...] = ()) -> dict:
    toolchain, apis = legacy_selection(kind, layers)
    return routes(toolchain, apis)


def rendered(toolchain: str | None = None, apis: list[str] | tuple[str, ...] = ()) -> str:
    return json.dumps(routes(toolchain, apis), indent=2, ensure_ascii=False) + "\n"


def target_for(root: Path) -> Path:
    return root / ".agents" / "skill-routes.json"


def skills_for(toolchain: str | None, apis: list[str] | tuple[str, ...], path: str) -> set[str]:
    """The required skills a write to `path` must load."""
    matched: set[str] = set()
    for route in routes(toolchain, apis)["routes"]:
        if re.search(route["path"], path):
            matched.update(route.get("skills") or [])
    return matched


def conditional_for(toolchain: str | None, apis: list[str] | tuple[str, ...], path: str) -> set[str]:
    """The conditional skills named for `path` that no matching route already requires."""
    matched: set[str] = set()
    for route in routes(toolchain, apis)["routes"]:
        if re.search(route["path"], path):
            matched.update(entry["skill"] for entry in route.get("conditional") or [])
    return matched - skills_for(toolchain, apis, path)


def write_or_check(toolchain: str | None, apis: list[str], root: Path, check: bool) -> int:
    target = target_for(root)
    expected = rendered(toolchain, apis)
    if check:
        actual = target.read_text(encoding="utf-8") if target.is_file() else None
        if actual != expected:
            print(f"STALE: {target}")
            return 1
        print(f"current: {target}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8", newline="\n")
    print(f"generated: {target} ({'+'.join(routes(toolchain, apis)['layers'])})")
    return 0


def self_test() -> int:
    profiles = [(None, []), ("gpp", []), ("msvc", []), (None, ["win32"]), ("gpp", ["win32"]), ("msvc", ["win32"])]
    with tempfile.TemporaryDirectory() as temporary:
        for index, (toolchain, apis) in enumerate(profiles):
            root = Path(temporary) / str(index)
            if write_or_check(toolchain, apis, root, False) or write_or_check(toolchain, apis, root, True):
                return 1
    if legacy_selection("windows") != ("msvc", ("win32",)) or legacy_selection("gcc") != ("gpp", ()):
        print("legacy profile normalization failed")
        return 1
    source = {"cpp:domain-design", "cpp:mixins", "cpp:structure"}
    cases = {
        ((None, ()), "src/main.cpp"): ({"cpp:style"}, source),
        (("msvc", ()), "src/main.cpp"): ({"cpp:style"}, source | {"msvc:toolchain"}),
        (("msvc", ()), "app/app.rc"): (set(), set()),
        ((None, ("win32",)), "src/main.cpp"): ({"cpp:style", "win32:style"}, source | {"win32:overview"}),
        ((None, ("win32",)), "app/app.vcxproj"): ({"win32:overview", "win32:style"}, set()),
        ((None, ("win32",)), "CMakeLists.txt"): ({"cpp:build", "cpp:structure", "win32:overview", "win32:style"}, {"cpp:libraries"}),
        (("gpp", ("win32",)), "src/main.cpp"): ({"cpp:style", "win32:style"}, source | {"gpp:toolchain", "win32:overview"}),
        (("gpp", ()), "CMakeLists.txt"): ({"cpp:build", "cpp:structure", "gpp:toolchain"}, {"cpp:libraries"}),
        ((None, ()), "tests/core_test.cpp"): ({"cpp:style", "cpp:testing"}, source),
        ((None, ()), "CMakeLists.txt"): ({"cpp:build", "cpp:structure"}, {"cpp:libraries"}),
        (("msvc", ()), "lib/lib.vcxproj"): ({"msvc:toolchain"}, set()),
        (("msvc", ()), "CMakePresets.json"): ({"cpp:build", "cpp:structure", "msvc:toolchain"}, {"cpp:libraries"}),
        (("msvc", ("win32",)), "app/app.vcxproj"): ({"msvc:toolchain", "win32:overview", "win32:style"}, set()),
    }
    for ((toolchain, apis), path), (required, conditional) in cases.items():
        actual = (skills_for(toolchain, apis, path), conditional_for(toolchain, apis, path))
        if actual != (required, conditional):
            print(f"unexpected skills for {toolchain}/{apis}:{path}: {actual}")
            return 1
    print("skill-route generator self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolchain", choices=TOOLCHAINS)
    parser.add_argument("--api", action="append", choices=APIS, default=[])
    parser.add_argument("--kind", choices=LEGACY_KINDS)
    parser.add_argument("--layer", action="append", choices=LEGACY_LAYERS, default=[])
    parser.add_argument("--into", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if any((args.toolchain, args.api, args.kind, args.layer, args.into, args.check)):
            parser.error("--self-test cannot be combined with generation arguments")
        return self_test()
    if args.kind and args.layer:
        parser.error("legacy --kind and --layer cannot be combined")
    if (args.kind or args.layer) and (args.toolchain or args.api):
        parser.error("legacy --kind/--layer cannot be combined with --toolchain/--api")
    if not args.into:
        parser.error("--into is required")
    toolchain, apis = legacy_selection(args.kind, args.layer) if (args.kind or args.layer) else normalize(args.toolchain, args.api)
    return write_or_check(toolchain, list(apis), args.into.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
