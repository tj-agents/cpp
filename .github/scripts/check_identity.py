import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


MARKETPLACE = "tj-agents"
MARKETPLACE_REPOSITORY = "tj-agents/marketplace"
CANONICAL_MARKETPLACES = [{"id": MARKETPLACE, "repository": MARKETPLACE_REPOSITORY}]
MARKETPLACE_FILES = (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")
LEGACY_MARKETPLACE = re.compile(r"(?<![\w.-])(?!tj-agents\b)[a-z0-9][a-z0-9-]*-agents\b", re.IGNORECASE)
SELECTOR = re.compile(r"(?<![\w.@/-])([a-z0-9][a-z0-9-]*)@([a-z0-9][a-z0-9-]*)(?![\w.@-])")
HISTORICAL = ("plans/", "contracts/", "CHANGELOG.md", "MIGRATION.md", "CPP_AGENTS_STRUCTURE_HANDOFF.md")
SELF_TEST = ".agents/tests/test_check_identity.py"


def is_harness(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return (len(parts) == 3 and parts[0] == "plugins" and parts[2] == "harness.json") or (
        path.startswith(".agents/plugins/manifests/harness/") and path.endswith(".json")
    )


def harness_package(path: str) -> str:
    relative = PurePosixPath(path)
    return relative.parts[1] if relative.parts[0] == "plugins" else relative.stem


def is_plugin_manifest(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return parts[-1:] == ("plugin.json",) and len(parts) >= 2 and parts[-2] in (".claude-plugin", ".codex-plugin")


def manifest_problems(path: str, document) -> list[str]:
    problems = []
    if path in MARKETPLACE_FILES and document.get("name") != MARKETPLACE:
        problems.append(f"{path}: marketplace name must be {MARKETPLACE}, found {document.get('name')!r}")
    if is_harness(path):
        identity = f"{MARKETPLACE}/{harness_package(path)}"
        if document.get("plugin") != identity:
            problems.append(f"{path}: plugin must be {identity}, found {document.get('plugin')!r}")
        requires = document.get("requires") or {}
        if requires.get("marketplaces") != CANONICAL_MARKETPLACES:
            problems.append(f"{path}: requires.marketplaces must be exactly {CANONICAL_MARKETPLACES}")
        for plugin in requires.get("plugins", []):
            if not isinstance(plugin, str) or not plugin.startswith(f"{MARKETPLACE}/"):
                problems.append(f"{path}: required plugin {plugin!r} is not a {MARKETPLACE}/<plugin> identity")
    if is_plugin_manifest(path):
        for dependency in document.get("dependencies", []):
            if not isinstance(dependency, str) or ("@" in dependency and not dependency.endswith(f"@{MARKETPLACE}")):
                problems.append(f"{path}: dependency {dependency!r} is not a <plugin>@{MARKETPLACE} identity")
    return problems


def text_problems(path: str, text: str, packages: set[str]) -> list[str]:
    problems = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in LEGACY_MARKETPLACE.finditer(line):
            problems.append(f"{path}:{number}: legacy marketplace name {match.group(0)!r}")
        for package, marketplace in SELECTOR.findall(line):
            if marketplace.lower() != MARKETPLACE and (package in packages or marketplace.lower().endswith("-agents")):
                problems.append(f"{path}:{number}: {package}@{marketplace} is not a <plugin>@{MARKETPLACE} identity")
    return problems


def problems(root: Path, files: list[str], packages: set[str]) -> list[str]:
    found = []
    for path in sorted(files):
        if path == SELF_TEST or path.startswith(HISTORICAL):
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if path.endswith(".json"):
            try:
                document = json.loads(text)
            except ValueError as error:
                found.append(f"{path}: unreadable JSON ({error})")
                continue
            if isinstance(document, dict):
                found.extend(manifest_problems(path, document))
        found.extend(text_problems(path, text, packages))
    for required in MARKETPLACE_FILES:
        if required not in files:
            found.append(f"{required}: missing marketplace file")
    return found


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, check=True,
    )
    return [name for name in result.stdout.decode("utf-8").split("\0") if name and (root / name).is_file()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    root = parser.parse_args().root.resolve()
    packages = set(json.loads((root / ".agents/plugins/payloads.json").read_text(encoding="utf-8"))["payloads"])
    files = tracked_files(root)
    found = problems(root, files, packages)
    for problem in found:
        print(problem, file=sys.stderr)
    if found:
        return 1
    print(f"every marketplace and plugin identity is {MARKETPLACE} across {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
