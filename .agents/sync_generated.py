#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys


FRONTMATTER = re.compile(r"\A---\n(?P<header>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
IDENTIFIER = re.compile(r"(?<![-/\w])([a-z][a-z0-9-]*:[a-z][a-z0-9-]*)(?![-\w])")
COMPATIBILITY_DEADLINE = "2027-03-31"
RETIRED_DOC_REFERENCE = re.compile(r"(?<![A-Za-z0-9_.-])(?:BUILD|DIRECTION|KNOWLEDGE|LEARNING|LIBRARIES|MSVC|OVERVIEW|SCAFFOLD|STYLE|TESTING|TOOLCHAIN|WIN32)\.md(?![A-Za-z0-9_/\\-]|\.(?!$|[\s)\]}>,\"`*]))")
EXPECTED_SCOPE_ROOTS = (".agents/base", ".agents/gpp", ".agents/msvc", ".agents/win32")
EXPECTED_HOST_ADAPTER_ROOTS = {"codex": ".codex/skills", "claude": ".claude/skills"}
EXPECTED_PACKAGE_ROOT = "plugins"
EXPECTED_MARKETPLACE_OUTPUTS = {"codex": ".agents/plugins/marketplace.json", "claude": ".claude-plugin/marketplace.json"}
RETIRED_GENERATED_ROOTS = (".agents/skills",)


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
            identifier = f"{scope['plugin']}:{name}"
            if identifier in found:
                raise ValueError(f"Duplicate public skill identifier: {identifier}")
            retired = retired_doc_references(body)
            if retired:
                raise ValueError(f"{path}: retired internal document reference(s): {', '.join(retired)}")
            found[identifier] = {
                "identifier": identifier,
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
        ancestor = resolved_root
        for part in relative.parts:
            ancestor = ancestor / part
            is_junction = getattr(ancestor, "is_junction", lambda: False)()
            if ancestor.is_symlink() or is_junction:
                raise ValueError(f"Generated root ancestor must not be a link or junction: {ancestor}")
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


def validated_retired_generated_roots(root: Path) -> list[Path]:
    resolved_root = root.resolve()
    result: list[Path] = []
    for value in RETIRED_GENERATED_ROOTS:
        relative = PurePosixPath(value)
        lexical = resolved_root.joinpath(*relative.parts)
        ancestor = resolved_root
        for part in relative.parts:
            ancestor = ancestor / part
            is_junction = getattr(ancestor, "is_junction", lambda: False)()
            if ancestor.is_symlink() or is_junction:
                raise ValueError(f"Retired generated root ancestor must not be a link or junction: {ancestor}")
        path = lexical.resolve()
        if path == resolved_root or not path.is_relative_to(resolved_root):
            raise ValueError(f"Retired generated root escapes or equals repository root: {value}")
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
    adapter_names = config["hostAdapterNames"]
    if set(adapter_names) != set(skills):
        raise ValueError("Host adapter names must map every canonical skill exactly once")
    if len(set(adapter_names.values())) != len(adapter_names) or any(not NAME.fullmatch(name) for name in adapter_names.values()):
        raise ValueError("Host adapter names must be unique valid flat skill names")
    for package, cfg in packages.items():
        if set(cfg["scopes"]) - scopes:
            raise ValueError(f"{package}: unknown scope")
        if payloads["payloads"][package] != cfg["scopes"]:
            raise ValueError(f"{package}: source and payload scope lists differ")
        owned = {identifier: skill for identifier, skill in skills.items() if skill["scope"] in cfg["scopes"]}
        names = cfg.get("skillNames", {})
        if set(names) - set(owned) or any(not NAME.fullmatch(name) for name in names.values()):
            raise ValueError(f"{package}: invalid source-to-package skill names")
        output_names = [names.get(identifier, skill["name"]) for identifier, skill in owned.items()]
        if len(output_names) != len(set(output_names)):
            raise ValueError(f"{package}: duplicate emitted skill name")
        for alias_name, alias in cfg.get("compatibilitySkillAliases", {}).items():
            if not NAME.fullmatch(alias_name) or alias_name in output_names or alias["source"] not in owned:
                raise ValueError(f"{package}: invalid compatibility skill alias {alias_name}")
            if alias.get("removeAfter") != COMPATIBILITY_DEADLINE:
                raise ValueError(f"{package}: compatibility skill alias must retain {COMPATIBILITY_DEADLINE}")
        for rewrites in (cfg.get("identifierRewrites", {}), cfg.get("hookIdentifierRewrites", {})):
            for source, target in rewrites.items():
                if source not in skills or not IDENTIFIER.fullmatch(target):
                    raise ValueError(f"{package}: invalid identifier rewrite {source}->{target}")
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
    if any(alias["removeAfter"] != COMPATIBILITY_DEADLINE for alias in aliases.values()):
        raise ValueError(f"Compatibility packages must retain {COMPATIBILITY_DEADLINE}")
    if packages["windows"]["scopes"] != ["msvc", "win32"]:
        raise ValueError("The compatibility windows package must retain both MSVC and Win32")
    if set(config["hook_packages"]) != set(payloads["hooks"]):
        raise ValueError("Hook package declarations differ")
    return [*public, *(name for name in packages if name not in public)]


def adapter_body(skill: dict, root_name: str, adapter_name: str) -> str:
    source = PurePosixPath(skill["relative"])
    adapter = PurePosixPath(root_name) / adapter_name / "SKILL.md"
    relative = PurePosixPath(os.path.relpath(source.as_posix(), adapter.parent.as_posix()).replace("\\", "/"))
    header = FRONTMATTER.match(skill["body"]).group("header")
    header = re.sub(r"(?m)^name:.*$", f"name: {adapter_name}", header, count=1)
    title = next((line for line in skill["body"].splitlines() if line.startswith("# ")), f"# {skill['name']}")
    return (
        f"---\n{header}\n---\n\n{title}\n\n"
        f"Read and follow the [canonical shared definition]({relative.as_posix()}) in full.\n"
        "This discovery entry is generated; edit the referenced `.agents/` definition.\n"
    )


def rewrite_identifiers(body: str, rewrites: dict[str, str]) -> str:
    # One pass avoids cascading replacements when a legacy name is also a source.
    return IDENTIFIER.sub(lambda match: rewrites.get(match.group(0), match.group(0)), body)


def package_body(skill: dict, package: str, cfg: dict, resources: list[dict]) -> tuple[str, str]:
    body = skill["body"]
    output_name = cfg.get("skillNames", {}).get(skill["identifier"], skill["name"])
    if output_name != skill["name"]:
        body = re.sub(rf"(?m)^name:\s*{re.escape(skill['name'])}\s*$", f"name: {output_name}", body, count=1)
    for old, new in cfg.get("contentRewrites", {}).get(skill["identifier"], {}).items():
        if old not in body:
            raise ValueError(f"{package}/{skill['name']}: compatibility content rewrite matched nothing")
        body = body.replace(old, new)
    body = rewrite_identifiers(body, cfg.get("identifierRewrites", {}))
    for resource in resources:
        if package not in resource["plugins"]:
            continue
        source_parent = PurePosixPath(skill["relative"]).parent
        relative = os.path.relpath(resource["source"], source_parent.as_posix()).replace("\\", "/")
        body = body.replace(f"{relative}/", f"../../{resource['destination']}/")
    return output_name, body


def compatibility_alias_body(skill: dict, alias_name: str, target_name: str, remove_after: str) -> str:
    return (
        f"---\nname: {alias_name}\ndescription: Compatibility alias for {skill['identifier']}; remove after {remove_after}.\n"
        f"kind: {skill['metadata']['kind']}\ndomain: {skill['metadata']['domain']}\n---\n\n"
        f"# Compatibility alias\n\nThis identifier is deprecated through {remove_after}.\n"
        f"Read and follow [{skill['identifier']}](../{target_name}/SKILL.md) in full.\n"
        "This redirect is generated; edit the canonical definition instead.\n"
    )


def route_generator(root: Path):
    # Scaffold route profiles are rendered by the same generator consumers run.
    spec = importlib.util.spec_from_file_location("gen_skill_routes", root / ".agents/gen_skill_routes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resource_bytes(path: Path, text: bool) -> bytes:
    if text:
        return read(path).encode("utf-8")
    return path.read_bytes()


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
            adapter_name = config["hostAdapterNames"][skill["identifier"]]
            emit(f"{adapter_root}/{adapter_name}/SKILL.md", adapter_body(skill, adapter_root, adapter_name))

    for scope in config["scopes"]:
        owned = sorted((item for item in skills.values() if item["scope"] == scope["name"]), key=lambda item: (item["metadata"]["kind"], item["name"]))
        lines = [f"# {scope['name']} capabilities", "", "Generated from canonical `.agents/` definitions.", ""]
        for item in owned:
            lines.append(f"- `{item['identifier']}` — {item['metadata']['kind']} — `{item['relative']}`")
        lines.append("")
        emit(f"{scope['root']}/INDEX.md", "\n".join(lines))

    for package in package_order:
        cfg = config["packages"][package]
        owned = [item for item in skills.values() if item["scope"] in cfg["scopes"]]
        emitted_names: set[str] = set()
        for skill in sorted(owned, key=lambda item: item["name"]):
            output_name, body = package_body(skill, package, cfg, config.get("resources", []))
            if output_name in emitted_names:
                raise ValueError(f"{package}: duplicate emitted skill {output_name}")
            emitted_names.add(output_name)
            emit(f"{package_root}/{package}/skills/{output_name}/SKILL.md", body)

        compatibility_aliases = {}
        for alias_name, alias in cfg.get("compatibilitySkillAliases", {}).items():
            skill = skills[alias["source"]]
            target_name = cfg.get("skillNames", {}).get(skill["identifier"], skill["name"])
            compatibility_aliases[alias_name] = {"replacedBy": f"{package}:{target_name}", "removeAfter": alias["removeAfter"]}
            emitted_names.add(alias_name)
            emit(f"{package_root}/{package}/skills/{alias_name}/SKILL.md", compatibility_alias_body(skill, alias_name, target_name, alias["removeAfter"]))

        for host, manifest_root in config["host_manifest_roots"].items():
            emit(f"{package_root}/{package}/.{host}-plugin/plugin.json", read(root / manifest_root / f"{package}.json"))

        index = [f"# {package} capabilities", "", "Generated from canonical `.agents/` definitions.", ""]
        for skill in sorted(owned, key=lambda item: item["name"]):
            output_name = cfg.get("skillNames", {}).get(skill["identifier"], skill["name"])
            index.append(f"- `{output_name}` — {skill['metadata']['kind']} — `{skill['relative']}`")
        index.append("")
        emit(f"{package_root}/{package}/INDEX.md", "\n".join(index))
        selection = {
            "plugin": package,
            "scopes": cfg["scopes"],
            "prerequisites": payloads.get("dependencies", {}).get(package, []),
            "skills": sorted(emitted_names),
        }
        if compatibility_aliases:
            selection["compatibilitySkillAliases"] = compatibility_aliases
        emit(f"{package_root}/{package}/selection.json", json.dumps(selection, indent=2) + "\n")

        if package in config["hook_packages"]:
            hook = read(root / ".agents/hooks/session_context.py")
            hook = rewrite_identifiers(hook, cfg.get("hookIdentifierRewrites", cfg.get("identifierRewrites", {})))
            for old, new in cfg.get("hookRewrites", {}).items():
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
                    emit(
                        f"{package_root}/{package}/{resource['destination']}/{suffix}",
                        resource_bytes(path, resource.get("text", False)),
                    )

    route_profiles = config.get("routeProfiles", [])
    if route_profiles:
        routes = route_generator(root)
        for profile in route_profiles:
            rendered = routes.rendered(profile["toolchain"], profile.get("apis", []))
            for package in profile["plugins"]:
                if package not in payloads["publicPlugins"]:
                    raise ValueError(f"Route profiles name canonical skills; {package} is not a canonical package")
                emit(f"{package_root}/{package}/{profile['destination']}", rendered)

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
    retired_roots = validated_retired_generated_roots(root)
    retired = sorted(path.relative_to(root).as_posix() for path in retired_roots if path.exists())
    stale = sorted(path for path in expected & actual if (root / path).read_bytes() != output[path])
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if check:
        for label, paths in (("MISSING", missing), ("STALE", stale), ("EXTRA", extra), ("RETIRED", retired)):
            for path in paths:
                print(f"{label}: {path}")
        if missing or stale or extra or retired:
            return 1
        print(f"generated outputs current: {len(expected)} files, {len(discover(root, config))} definitions")
        return 0

    for path in [*validated_generated_roots(root, config), *retired_roots]:
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


PACKAGE_VERSIONS = ".agents/plugins/package-versions.json"


def package_state(root: Path, package: str) -> tuple[str, str]:
    """Return a package's manifest version and a digest of everything else it ships."""
    package_root = root / EXPECTED_PACKAGE_ROOT / package
    versions: set[str] = set()
    digest = hashlib.sha256()
    for path in sorted(package_root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(package_root).as_posix()
        data = path.read_bytes()
        if relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            manifest = json.loads(data)
            versions.add(manifest.pop("version"))
            data = json.dumps(manifest, sort_keys=True).encode("utf-8")
        digest.update(relative.encode("utf-8") + b"\0" + hashlib.sha256(data).digest())
    if len(versions) != 1:
        raise ValueError(f"{package}: host manifests disagree on the version: {sorted(versions)}")
    return versions.pop(), digest.hexdigest()


def record_package_versions(root: Path) -> int:
    # Append-only: a published version's content can never be re-recorded.
    path = root / PACKAGE_VERSIONS
    recorded = load(path) if path.is_file() else {}
    payloads = load(root / ".agents/plugins/payloads.json")
    for package in sorted(payloads["payloads"]):
        version, digest = package_state(root, package)
        history = recorded.setdefault(package, {})
        if history.get(version, digest) != digest:
            print(f"{package}: content changed without a version bump from {version}")
            return 1
        history[version] = digest
    path.write_text(json.dumps(recorded, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"recorded package versions: {path.relative_to(root).as_posix()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--record-package-versions", action="store_true")
    args = parser.parse_args()
    if args.record_package_versions:
        return record_package_versions(args.root.resolve())
    return synchronize(args.root.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
