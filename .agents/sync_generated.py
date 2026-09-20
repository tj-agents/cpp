#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys


FRONTMATTER = re.compile(r"\A---\n(?P<header>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
RETIRED_DOC_REFERENCE = re.compile(r"(?<![A-Za-z0-9_.-])(?:BUILD|DIRECTION|KNOWLEDGE|LEARNING|LIBRARIES|MSVC|OVERVIEW|SCAFFOLD|STYLE|TESTING|TOOLCHAIN|WIN32)\.md(?=$|[#?\s)\]}>,\"`;:]|\.(?=$|\s))")
EXPECTED_SCOPE_ROOTS = (".agents/base", ".agents/gpp", ".agents/msvc", ".agents/win32")
EXPECTED_HOST_ADAPTER_ROOTS = {"agents": ".agents/skills", "codex": ".codex/skills", "claude": ".claude/skills"}
EXPECTED_PACKAGE_ROOT = "plugins"
EXPECTED_MARKETPLACE_OUTPUTS = {"codex": ".agents/plugins/marketplace.json", "claude": ".claude-plugin/marketplace.json"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def load(path: Path):
    return json.loads(read(path))


def metadata(body: str, source: Path) -> dict[str, str]:
    match = FRONTMATTER.match(body)
    if match is None:
        raise ValueError(f"Missing frontmatter: {source}")
    values: dict[str, str] = {}
    for line in match.group("header").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    for field in ("name", "description", "kind", "domain"):
        if not values.get(field):
            raise ValueError(f"{source}: missing {field}")
    if not NAME.fullmatch(values["name"]):
        raise ValueError(f"{source}: invalid skill name {values['name']}")
    return values


def discover(root: Path, config: dict) -> dict[str, dict]:
    found: dict[str, dict] = {}
    scopes = {scope["name"]: scope for scope in config["scopes"]}
    if set(scopes) != {"base", "gpp", "msvc", "win32"}:
        raise ValueError("sources.json must declare base, gpp, msvc, and win32 exactly once")
    for scope in config["scopes"]:
        source_root = root / scope["root"]
        if not source_root.is_dir() or scope["layout"] != "kind":
            raise ValueError(f"Invalid canonical scope: {scope}")
        for path in sorted(source_root.glob("*/*/SKILL.md")):
            body = read(path)
            values = metadata(body, path)
            name = values["name"]
            if name != path.parent.name:
                raise ValueError(f"{path}: folder and public skill name differ")
            if values["kind"] != path.parent.parent.name:
                raise ValueError(f"{path}: kind metadata and folder differ")
            if values["domain"] != scope["domain"]:
                raise ValueError(f"{path}: domain does not match scope declaration")
            if name in found:
                raise ValueError(f"Duplicate public skill name: {name}")
            retired = retired_doc_references(body)
            if retired:
                raise ValueError(f"{path}: retired internal document reference(s): {', '.join(retired)}")
            found[name] = {
                "name": name,
                "body": body,
                "metadata": values,
                "scope": scope["name"],
                "relative": path.relative_to(root).as_posix(),
            }
    if not found:
        raise ValueError("No canonical skills discovered")
    return found


def expected_generated_roots(config: dict) -> set[str]:
    scope_roots = tuple(scope["root"] for scope in config["scopes"])
    if scope_roots != EXPECTED_SCOPE_ROOTS:
        raise ValueError(f"Scope roots must remain repository-owned paths: {EXPECTED_SCOPE_ROOTS}")
    if config["host_adapter_roots"] != EXPECTED_HOST_ADAPTER_ROOTS:
        raise ValueError(f"Host adapter roots must remain repository-owned paths: {EXPECTED_HOST_ADAPTER_ROOTS}")
    if config["package_root"] != EXPECTED_PACKAGE_ROOT:
        raise ValueError(f"Package root must remain the repository-owned path: {EXPECTED_PACKAGE_ROOT}")
    if config["marketplace_outputs"] != EXPECTED_MARKETPLACE_OUTPUTS:
        raise ValueError(f"Marketplace outputs must remain repository-owned paths: {EXPECTED_MARKETPLACE_OUTPUTS}")
    return {
        *EXPECTED_HOST_ADAPTER_ROOTS.values(),
        EXPECTED_PACKAGE_ROOT,
        *EXPECTED_MARKETPLACE_OUTPUTS.values(),
        *(f"{scope_root}/INDEX.md" for scope_root in EXPECTED_SCOPE_ROOTS),
    }


def retired_doc_references(body: str) -> list[str]:
    return sorted(set(RETIRED_DOC_REFERENCE.findall(body)))


def validated_generated_roots(root: Path, config: dict) -> list[Path]:
    declared = config["generated_roots"]
    expected = expected_generated_roots(config)
    if len(declared) != len(set(declared)) or set(declared) != expected:
        missing = sorted(expected - set(declared))
        extra = sorted(set(declared) - expected)
        raise ValueError(f"Generated roots disagree with the source map; missing={missing}, extra={extra}")
    resolved_root = root.resolve()
    allowed_indexes = {
        (resolved_root / scope["root"] / "INDEX.md").resolve()
        for scope in config["scopes"]
    }
    authored = [
        *(resolved_root / scope["root"] for scope in config["scopes"]),
        *(resolved_root / value for value in config["host_manifest_roots"].values()),
        resolved_root / ".agents/hooks",
        resolved_root / ".agents/plugins/sources.json",
        resolved_root / ".agents/plugins/payloads.json",
        *(resolved_root / resource["source"] for resource in config.get("resources", [])),
    ]
    result: list[Path] = []
    for value in declared:
        relative = PurePosixPath(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid generated root: {value}")
        lexical = resolved_root.joinpath(*relative.parts)
        path = lexical.resolve()
        if path == resolved_root or not path.is_relative_to(resolved_root):
            raise ValueError(f"Generated root escapes or equals repository root: {value}")
        if lexical.is_symlink():
            raise ValueError(f"Generated root must not be a symlink: {value}")
        overlaps = [source for source in authored if path == source or path.is_relative_to(source) or source.is_relative_to(path)]
        if overlaps and path not in allowed_indexes:
            names = ", ".join(source.relative_to(resolved_root).as_posix() for source in overlaps)
            raise ValueError(f"Generated root overlaps authored source ({names}): {value}")
        result.append(path)
    return result


def validate(root: Path, config: dict, payloads: dict, skills: dict[str, dict]) -> list[str]:
    validated_generated_roots(root, config)
    packages = config["packages"]
    public = payloads["publicPlugins"]
    if public != ["cpp", "gpp", "msvc", "win32"]:
        raise ValueError("Public plugin order must be cpp, gpp, msvc, win32")
    if set(packages) != set(payloads["payloads"]):
        raise ValueError("sources.json packages and payloads.json payloads differ")
    scopes = {scope["name"] for scope in config["scopes"]}
    for package, cfg in packages.items():
        if set(cfg["scopes"]) - scopes:
            raise ValueError(f"{package}: unknown scope")
        if payloads["payloads"][package] != cfg["scopes"]:
            raise ValueError(f"{package}: source and payload scope lists differ")
        for alias_from, alias_to in cfg.get("skillAliases", {}).items():
            if alias_from not in skills or not NAME.fullmatch(alias_to):
                raise ValueError(f"{package}: invalid skill alias {alias_from}->{alias_to}")
        for host, manifest_root in config["host_manifest_roots"].items():
            manifest_path = root / manifest_root / f"{package}.json"
            manifest = load(manifest_path)
            if manifest.get("name") != package or manifest.get("skills") != "./skills/":
                raise ValueError(f"{manifest_path}: invalid name or skills root")
    for package, dependencies in payloads.get("dependencies", {}).items():
        if package not in packages or set(dependencies) - set(packages):
            raise ValueError(f"{package}: invalid dependencies")
    aliases = payloads["compatibilityAliases"]
    if set(aliases) != {"base", "gcc", "windows", "cpp-standards", "gpp-standards"}:
        raise ValueError("Compatibility package roster changed")
    if set(config["hook_packages"]) != set(payloads["hooks"]):
        raise ValueError("Hook package declarations differ")
    return [*public, *(name for name in packages if name not in public)]


def adapter_body(skill: dict, root_name: str) -> str:
    source = PurePosixPath(skill["relative"])
    adapter = PurePosixPath(root_name) / skill["name"] / "SKILL.md"
    relative = PurePosixPath(os.path.relpath(source.as_posix(), adapter.parent.as_posix()).replace("\\", "/"))
    header = FRONTMATTER.match(skill["body"]).group("header")
    title = next((line for line in skill["body"].splitlines() if line.startswith("# ")), f"# {skill['name']}")
    return (
        f"---\n{header}\n---\n\n{title}\n\n"
        f"Read and follow the [canonical shared definition]({relative.as_posix()}) in full.\n"
        "This discovery entry is generated; edit the referenced `.agents/` definition.\n"
    )


def package_body(skill: dict, package: str, cfg: dict) -> tuple[str, str]:
    body = skill["body"]
    output_name = cfg.get("skillAliases", {}).get(skill["name"], skill["name"])
    if output_name != skill["name"]:
        body = re.sub(rf"(?m)^name:\s*{re.escape(skill['name'])}\s*$", f"name: {output_name}", body, count=1)
    for old, new in cfg.get("contentRewrites", {}).get(skill["name"], {}).items():
        if old not in body:
            raise ValueError(f"{package}/{skill['name']}: compatibility content rewrite matched nothing")
        body = body.replace(old, new)
    for old, new in cfg.get("rewrites", {}).items():
        body = body.replace(old, new)
    if skill["name"] == "msvc-scaffold":
        body = body.replace("../scripts/", "../../resources/msvc/utility/scripts/")
        body = body.replace("<skill-directory>/../scripts/", "<skill-directory>/../../resources/msvc/utility/scripts/")
    return output_name, body


def build(root: Path) -> tuple[dict[str, bytes], dict]:
    config = load(root / ".agents/plugins/sources.json")
    payloads = load(root / ".agents/plugins/payloads.json")
    skills = discover(root, config)
    package_order = validate(root, config, payloads, skills)
    output: dict[str, bytes] = {}
    package_root = config["package_root"].rstrip("/")

    def emit(relative: str, data: str | bytes):
        relative = PurePosixPath(relative).as_posix()
        if relative in output:
            raise ValueError(f"Duplicate generated output: {relative}")
        output[relative] = data.encode("utf-8") if isinstance(data, str) else data

    for adapter_root in config["host_adapter_roots"].values():
        for skill in skills.values():
            emit(f"{adapter_root}/{skill['name']}/SKILL.md", adapter_body(skill, adapter_root))

    for scope in config["scopes"]:
        owned = sorted((item for item in skills.values() if item["scope"] == scope["name"]), key=lambda item: (item["metadata"]["kind"], item["name"]))
        lines = [f"# {scope['name']} capabilities", "", "Generated from canonical `.agents/` definitions.", ""]
        for item in owned:
            lines.append(f"- `{item['name']}` — {item['metadata']['kind']} — `{item['relative']}`")
        lines.append("")
        emit(f"{scope['root']}/INDEX.md", "\n".join(lines))

    for package in package_order:
        cfg = config["packages"][package]
        owned = [item for item in skills.values() if item["scope"] in cfg["scopes"]]
        emitted_names: set[str] = set()
        for skill in sorted(owned, key=lambda item: item["name"]):
            output_name, body = package_body(skill, package, cfg)
            if output_name in emitted_names:
                raise ValueError(f"{package}: duplicate emitted skill {output_name}")
            emitted_names.add(output_name)
            emit(f"{package_root}/{package}/skills/{output_name}/SKILL.md", body)

        for host, manifest_root in config["host_manifest_roots"].items():
            emit(f"{package_root}/{package}/.{host}-plugin/plugin.json", read(root / manifest_root / f"{package}.json"))

        index = [f"# {package} capabilities", "", "Generated from canonical `.agents/` definitions.", ""]
        for skill in sorted(owned, key=lambda item: item["name"]):
            output_name = cfg.get("skillAliases", {}).get(skill["name"], skill["name"])
            index.append(f"- `{output_name}` — {skill['metadata']['kind']} — `{skill['relative']}`")
        index.append("")
        emit(f"{package_root}/{package}/INDEX.md", "\n".join(index))
        selection = {
            "plugin": package,
            "scopes": cfg["scopes"],
            "prerequisites": payloads.get("dependencies", {}).get(package, []),
            "skills": sorted(emitted_names),
        }
        emit(f"{package_root}/{package}/selection.json", json.dumps(selection, indent=2) + "\n")

        if package in config["hook_packages"]:
            hook = read(root / ".agents/hooks/session_context.py")
            for old, new in cfg.get("hookRewrites", cfg.get("rewrites", {})).items():
                hook = hook.replace(old, new)
            emit(f"{package_root}/{package}/hooks/session_context.py", hook)
            emit(f"{package_root}/{package}/hooks/hooks.json", read(root / ".agents/hooks/hooks.json"))

    for resource in config.get("resources", []):
        source = root / resource["source"]
        for package in resource["plugins"]:
            if package not in config["packages"]:
                raise ValueError(f"Unknown resource package: {package}")
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    suffix = path.relative_to(source).as_posix()
                    emit(f"{package_root}/{package}/{resource['destination']}/{suffix}", path.read_bytes())

    codex_plugins = []
    claude_plugins = []
    for package in package_order:
        codex_plugins.append({
            "name": package,
            "source": {"source": "local", "path": f"./{package_root}/{package}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
        claude_plugins.append({"name": package, "source": f"./{package_root}/{package}"})
    emit(config["marketplace_outputs"]["codex"], json.dumps({"name": "cpp-agents", "interface": {"displayName": "C++ Agents"}, "plugins": codex_plugins}, indent=2) + "\n")
    emit(config["marketplace_outputs"]["claude"], json.dumps({"name": "cpp-agents", "description": payloads["description"], "owner": {"name": "Tommy Seery"}, "plugins": claude_plugins}, indent=2) + "\n")
    return output, config


def existing_files(root: Path, generated_roots: list[str]) -> set[str]:
    result: set[str] = set()
    for value in generated_roots:
        path = root / value
        if path.is_dir():
            for item in path.rglob("*"):
                if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc":
                    result.add(item.relative_to(root).as_posix())
        elif path.is_file():
            result.add(path.relative_to(root).as_posix())
    return result


def synchronize(root: Path, check: bool) -> int:
    output, config = build(root)
    expected = set(output)
    actual = existing_files(root, config["generated_roots"])
    stale = sorted(path for path in expected & actual if (root / path).read_bytes() != output[path])
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if check:
        for label, paths in (("MISSING", missing), ("STALE", stale), ("EXTRA", extra)):
            for path in paths:
                print(f"{label}: {path}")
        if missing or stale or extra:
            return 1
        print(f"generated outputs current: {len(expected)} files, {len(discover(root, config))} definitions")
        return 0

    for path in validated_generated_roots(root, config):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for relative, data in output.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"generated {len(expected)} files from {len(discover(root, config))} definitions")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return synchronize(args.root.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
