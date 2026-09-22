import importlib.util
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PAYLOADS = ROOT / ".agents" / "plugins" / "payloads.json"
SKILL_CONTRACT = ROOT / ".agents" / "plugins" / "skill-contract.json"
SOURCES = ROOT / ".agents" / "plugins" / "sources.json"
GENERATOR = ROOT / ".agents" / "gen_skill_routes.py"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_text_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_skill_routes", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_object_id(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_tree_id(entries: list[str]) -> str:
    content = bytearray()
    for entry in entries:
        metadata, name = entry.split("\t", 1)
        mode, _kind, object_id = metadata.split(" ")
        content.extend(mode.lstrip("0").encode("ascii"))
        content.extend(b" ")
        content.extend(name.encode("utf-8"))
        content.extend(b"\0")
        content.extend(bytes.fromhex(object_id))
    return git_object_id("tree", bytes(content))


def entry_id(entries: list[str], name: str) -> str:
    for entry in entries:
        metadata, entry_name = entry.split("\t", 1)
        if entry_name == name:
            return metadata.rsplit(" ", 1)[1]
    raise AssertionError(f"missing signed tree entry: {name}")


def gpg_home(path: Path) -> str:
    if os.name != "nt":
        return str(path)
    resolved = path.resolve()
    return f"/{resolved.drive[0].lower()}{resolved.as_posix()[2:]}"


def find_gpg() -> str:
    found = shutil.which("gpg")
    if found:
        return found
    git = shutil.which("git")
    if git and os.name == "nt":
        candidate = Path(git).resolve().parents[1] / "usr" / "bin" / "gpg.exe"
        if candidate.is_file():
            return str(candidate)
    raise AssertionError("GPG is required to verify the pinned external commit signature")


class MarketplaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.marketplace = read_json(MARKETPLACE)
        cls.payloads = read_json(PAYLOADS)
        cls.contract = read_json(SKILL_CONTRACT)
        cls.sources = read_json(SOURCES)
        cls.generator = load_generator()

    def test_public_plugins_are_the_four_independent_scopes_in_order(self) -> None:
        self.assertEqual(["cpp", "gpp", "msvc", "win32"], self.payloads["publicPlugins"])
        names = [plugin["name"] for plugin in self.marketplace["plugins"]]
        self.assertEqual(self.payloads["publicPlugins"], names[:4])

    def test_every_marketplace_entry_has_a_matching_manifest_and_payload(self) -> None:
        for entry in self.marketplace["plugins"]:
            name = entry["name"]
            manifest_path = ROOT / entry["source"]["path"] / ".codex-plugin" / "plugin.json"
            manifest = read_json(manifest_path)
            self.assertEqual(name, manifest["name"])
            self.assertIn(name, self.payloads["payloads"])

    def test_layer_dependencies_exist_and_are_acyclic(self) -> None:
        names = set(self.payloads["payloads"])
        dependencies = self.payloads["dependencies"]
        self.assertEqual(["cpp"], dependencies["gpp"])
        self.assertEqual(["cpp"], dependencies["msvc"])
        self.assertEqual(["cpp"], dependencies["win32"])
        self.assertEqual(["base"], dependencies["windows"])
        self.assertEqual(["base"], dependencies["gcc"])
        for plugin, required in dependencies.items():
            self.assertIn(plugin, names)
            self.assertNotIn(plugin, required)
            self.assertTrue(set(required) <= names)

        def visit(plugin: str, active: set[str], complete: set[str]) -> None:
            if plugin in active:
                self.fail(f"plugin dependency cycle includes {plugin}")
            if plugin in complete:
                return
            active.add(plugin)
            for dependency in dependencies.get(plugin, []):
                visit(dependency, active, complete)
            active.remove(plugin)
            complete.add(plugin)

        complete: set[str] = set()
        for name in names:
            visit(name, set(), complete)

    def test_compatibility_aliases_are_time_bounded_and_not_public(self) -> None:
        public = set(self.payloads["publicPlugins"])
        aliases = self.payloads["compatibilityAliases"]
        self.assertEqual({"base", "gcc", "windows", "cpp-standards", "gpp-standards"}, set(aliases))
        for name, alias in aliases.items():
            self.assertNotIn(name, public)
            replacements = alias["replacedBy"] if isinstance(alias["replacedBy"], list) else [alias["replacedBy"]]
            self.assertTrue(set(replacements) <= public)
            self.assertGreaterEqual(date.fromisoformat(alias["removeAfter"]), date.today())
        self.assertEqual(["msvc", "win32"], aliases["windows"]["replacedBy"])
        self.assertTrue(aliases["windows"]["requiresExplicitSplit"])

    def test_generated_routes_reference_real_skill_contracts(self) -> None:
        scope_plugins = {scope["name"]: scope["plugin"] for scope in self.sources["scopes"]}
        inventory = {}
        for scope in self.sources["scopes"]:
            for skill_file in (ROOT / scope["root"]).glob("*/*/SKILL.md"):
                inventory[(scope_plugins[scope["name"]], skill_file.parent.name)] = skill_file
        profiles = [(None, []), ("gpp", []), ("msvc", []), (None, ["win32"]), ("gpp", ["win32"]), ("msvc", ["win32"])]
        for toolchain, apis in profiles:
            for route in self.generator.routes(toolchain, apis)["routes"]:
                for identifier in route.get("skills", []):
                    plugin, skill = identifier.split(":", 1)
                    self.assertIn((plugin, skill), inventory, identifier)
                    self.assertIn(plugin, self.payloads["publicPlugins"])
        all_routes = json.dumps([self.generator.routes(toolchain, apis) for toolchain, apis in profiles])
        self.assertNotIn("concertable:", all_routes)

    def test_short_canonical_names_and_published_legacy_identifiers_coexist(self) -> None:
        canonical = {
            "cpp": {"build", "style", "structure", "testing", "libraries", "direction", "knowledge", "learning", "domain-design"},
            "gpp": {"toolchain", "scaffold"},
            "msvc": {"toolchain", "scaffold"},
            "win32": {"style", "knowledge", "overview"},
        }
        legacy = {
            "cpp": {"cpp-build", "cpp-style", "cpp-structure", "cpp-testing", "cpp-libraries", "cpp-direction", "cpp-knowledge", "cpp-learning"},
            "gpp": {"gpp-toolchain", "gpp-scaffold"},
            "msvc": {"msvc-toolchain", "msvc-scaffold"},
            "win32": {"win32-style", "windows-cpp-knowledge", "windows-overview"},
        }
        for scope in self.sources["scopes"]:
            plugin = scope["plugin"]
            authored = {path.parent.name for path in (ROOT / scope["root"]).glob("*/*/SKILL.md")}
            self.assertEqual(canonical[plugin], authored)
            packaged = {path.parent.name for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")}
            self.assertEqual(canonical[plugin] | legacy[plugin], packaged)
        expected_legacy_packages = {
            "base": legacy["cpp"] | {"domain-design"},
            "cpp-standards": legacy["cpp"] | {"domain-design"},
            "gcc": {"gcc-toolchain", "gpp-scaffold"},
            "gpp-standards": legacy["gpp"],
            "windows": legacy["msvc"] | legacy["win32"],
        }
        for plugin, expected in expected_legacy_packages.items():
            inventory = {path.parent.name for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")}
            self.assertEqual(expected, inventory, plugin)
            self.assertEqual(expected, set(self.payloads["compatibilityAliases"][plugin]["skillAliases"]))

    def test_canonical_compatibility_aliases_are_dated_local_redirects(self) -> None:
        for plugin in self.payloads["publicPlugins"]:
            package = ROOT / "plugins" / plugin
            selection = read_json(package / "selection.json")
            aliases = self.sources["packages"][plugin]["compatibilitySkillAliases"]
            self.assertEqual(set(aliases), set(selection["compatibilitySkillAliases"]))
            for alias_name, alias in aliases.items():
                alias_file = package / "skills" / alias_name / "SKILL.md"
                body = alias_file.read_text(encoding="utf-8")
                self.assertIn(f"name: {alias_name}\n", body)
                self.assertEqual("2027-03-31", alias["removeAfter"])
                self.assertIn(alias["removeAfter"], body)
                self.assertIn(alias["source"], body)
                link = re.search(r"\]\(([^)]+)\)", body)
                self.assertIsNotNone(link)
                target = (alias_file.parent / link.group(1)).resolve()
                self.assertTrue(target.is_file(), target)
                self.assertTrue(target.is_relative_to(package.resolve()))
                self.assertEqual(alias["source"].split(":", 1)[1], target.parent.name)
                self.assertEqual({"replacedBy": alias["source"], "removeAfter": "2027-03-31"}, selection["compatibilitySkillAliases"][alias_name])

    def test_flat_host_adapter_names_resolve_each_qualified_source(self) -> None:
        scope_roots = {scope["plugin"]: ROOT / scope["root"] for scope in self.sources["scopes"]}
        adapter_names = self.sources["hostAdapterNames"]
        self.assertEqual(len(adapter_names), len(set(adapter_names.values())))
        for adapter_root in self.sources["host_adapter_roots"].values():
            for identifier, adapter_name in adapter_names.items():
                plugin, name = identifier.split(":", 1)
                adapter = ROOT / adapter_root / adapter_name / "SKILL.md"
                body = adapter.read_text(encoding="utf-8")
                self.assertIn(f"name: {adapter_name}\n", body)
                link = re.search(r"canonical shared definition\]\(([^)]+)\)", body)
                self.assertIsNotNone(link)
                target = (adapter.parent / link.group(1)).resolve()
                self.assertTrue(target.is_file(), target)
                self.assertTrue(target.is_relative_to(scope_roots[plugin].resolve()))
                self.assertEqual(name, target.parent.name)

    def test_scaffold_links_resolve_inside_every_standalone_package(self) -> None:
        cases = {
            "gpp": ("scaffold", "gpp", "new-gpp-project.sh"),
            "gcc": ("gpp-scaffold", "gpp", "new-gpp-project.sh"),
            "gpp-standards": ("gpp-scaffold", "gpp", "new-gpp-project.sh"),
            "msvc": ("scaffold", "msvc", "New-MsvcProject.ps1"),
            "windows": ("msvc-scaffold", "msvc", "New-MsvcProject.ps1"),
        }
        for plugin, (name, scope, script) in cases.items():
            package = ROOT / "plugins" / plugin
            skill = package / "skills" / name / "SKILL.md"
            body = skill.read_text(encoding="utf-8")
            link = re.search(r"\[" + re.escape(script) + r"\]\(([^)]+)\)", body)
            self.assertIsNotNone(link, plugin)
            target = (skill.parent / link.group(1)).resolve()
            self.assertTrue(target.is_file(), target)
            self.assertTrue(target.is_relative_to(package.resolve()))
            self.assertEqual((package / "resources" / scope / "utility/scripts" / script).resolve(), target)
            self.assertIn(f"<skill-directory>/{link.group(1)}", body)

    def test_external_skill_contract_matches_pinned_agent_standards_source(self) -> None:
        source_value = os.environ.get("AGENT_STANDARDS_SOURCE")
        if not source_value:
            self.skipTest("set AGENT_STANDARDS_SOURCE for an optional live-checkout comparison")

        source = Path(source_value).resolve()
        contract = self.contract["externalPlugins"]["concertable"]
        revision = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout.strip()
        self.assertEqual(contract["sourceCommit"], revision)

        origin = subprocess.run(
            ["git", "-C", str(source), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout.strip()
        repository_match = re.fullmatch(
            r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?",
            origin,
        )
        self.assertIsNotNone(repository_match, origin)
        expected_slug = contract["repository"].removeprefix("https://github.com/").removesuffix(".git")
        self.assertEqual(expected_slug.casefold(), repository_match.group(1).casefold())
        remote_revision = subprocess.run(
            ["gh", "api", f"repos/{expected_slug}/commits/{revision}", "--jq", ".sha"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout.strip()
        self.assertEqual(revision, remote_revision)

        def source_bytes(relative_path: str) -> bytes:
            return subprocess.run(
                ["git", "-C", str(source), "show", f"{revision}:{relative_path}"],
                capture_output=True,
                check=True,
            ).stdout

        manifest_bytes = source_bytes(contract["manifest"])
        manifest = json.loads(manifest_bytes)
        self.assertEqual("concertable", manifest["name"])
        self.assertEqual(contract["version"], manifest["version"])
        self.assertEqual(contract["repository"], manifest["repository"])
        self.assertEqual(
            contract["manifestSha256"],
            hashlib.sha256(manifest_bytes).hexdigest(),
        )
        for skill in contract["skills"]:
            skill_bytes = source_bytes(f"{contract['skillsRoot']}/{skill}/SKILL.md")
            self.assertEqual(
                contract["skillSha256"][skill],
                hashlib.sha256(skill_bytes).hexdigest(),
            )

    def test_external_skill_contract_has_immutable_source_evidence(self) -> None:
        git_commit = re.compile(r"^[0-9a-f]{40}$")
        digest = re.compile(r"^[0-9a-f]{64}$")
        for contract in self.contract["externalPlugins"].values():
            self.assertRegex(contract["sourceCommit"], git_commit)
            self.assertRegex(contract["manifestSha256"], digest)
            self.assertEqual(set(contract["skills"]), set(contract["skillSha256"]))
            for value in contract["skillSha256"].values():
                self.assertRegex(value, digest)

    def test_external_skill_contract_has_signed_source_provenance(self) -> None:
        contract = self.contract["externalPlugins"]["concertable"]
        evidence_root = ROOT / contract["provenance"]
        provenance = read_json(evidence_root / "provenance.json")
        self.assertEqual(contract["sourceCommit"], provenance["sourceCommit"])

        trees = provenance["trees"]
        tree_ids = {name: git_tree_id(entries) for name, entries in trees.items()}
        self.assertEqual(provenance["rootTree"], tree_ids["root"])
        self.assertEqual(tree_ids["plugins"], entry_id(trees["root"], "plugins"))
        self.assertEqual(tree_ids["concertable"], entry_id(trees["plugins"], "concertable"))
        self.assertEqual(tree_ids["codex-plugin"], entry_id(trees["concertable"], ".codex-plugin"))
        self.assertEqual(tree_ids["codex-skills"], entry_id(trees["concertable"], "codex-skills"))

        manifest_bytes = canonical_text_bytes(evidence_root / "plugin.json")
        self.assertEqual(provenance["manifestBlob"], git_object_id("blob", manifest_bytes))
        self.assertEqual(provenance["manifestBlob"], entry_id(trees["codex-plugin"], "plugin.json"))
        self.assertEqual(contract["manifestSha256"], hashlib.sha256(manifest_bytes).hexdigest())
        manifest = json.loads(manifest_bytes)
        self.assertEqual("concertable", manifest["name"])
        self.assertEqual(contract["version"], manifest["version"])
        self.assertEqual(contract["repository"], manifest["repository"])

        self.assertEqual(set(contract["skills"]), set(provenance["skillBlobs"]))
        for skill, blob_id in provenance["skillBlobs"].items():
            self.assertEqual(tree_ids[skill], entry_id(trees["codex-skills"], skill))
            self.assertEqual(blob_id, entry_id(trees[skill], "SKILL.md"))
            skill_bytes = canonical_text_bytes(evidence_root / "skills" / skill / "SKILL.md")
            self.assertEqual(blob_id, git_object_id("blob", skill_bytes))
            self.assertEqual(contract["skillSha256"][skill], hashlib.sha256(skill_bytes).hexdigest())
            front_matter = skill_bytes.decode("utf-8").split("---", 2)[1]
            fields = {
                key: value
                for line in front_matter.splitlines()
                if ":" in line
                for key, value in [line.split(":", 1)]
            }
            self.assertEqual(skill, fields.get("name", "").strip())
            self.assertTrue(fields.get("description", "").strip())

        commit_bytes = canonical_text_bytes(evidence_root / "commit.txt")
        if not provenance["commitObjectEndsWithNewline"]:
            self.assertTrue(commit_bytes.endswith(b"\n"))
            commit_bytes = commit_bytes[:-1]
        self.assertEqual(contract["sourceCommit"], git_object_id("commit", commit_bytes))
        self.assertIn(f"tree {provenance['rootTree']}\n".encode("ascii"), commit_bytes)

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            keyring = temporary / "gnupg"
            keyring.mkdir()
            environment = os.environ.copy()
            environment["GNUPGHOME"] = gpg_home(keyring)
            environment["GIT_CONFIG_NOSYSTEM"] = "1"
            environment["GIT_CONFIG_GLOBAL"] = os.devnull
            gpg = find_gpg()
            key_file = evidence_root / "github-web-flow.asc"
            keys = subprocess.run(
                [gpg, "--with-colons", "--import-options", "show-only", "--import", str(key_file)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                check=True,
            ).stdout
            fingerprints = {
                line.split(":")[9]
                for line in keys.splitlines()
                if line.startswith("fpr:")
            }
            self.assertIn(provenance["signingKeyFingerprint"], fingerprints)
            subprocess.run([gpg, "--batch", "--import", str(key_file)], env=environment, check=True)

            repository = temporary / "repository"
            repository.mkdir()
            subprocess.run(["git", "init", "--quiet"], cwd=repository, env=environment, check=True)
            written = subprocess.run(
                ["git", "hash-object", "-w", "-t", "commit", "--stdin"],
                input=commit_bytes,
                capture_output=True,
                cwd=repository,
                env=environment,
                check=True,
            ).stdout.decode("ascii").strip()
            self.assertEqual(contract["sourceCommit"], written)
            verification = subprocess.run(
                [
                    "git",
                    "-c", "gpg.format=openpgp",
                    "-c", f"gpg.program={Path(gpg).as_posix()}",
                    "verify-commit", "--raw", contract["sourceCommit"],
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=repository,
                env=environment,
                check=True,
            )
            status = verification.stdout + verification.stderr
            valid_signers = {
                line.split()[2]
                for line in status.splitlines()
                if "[GNUPG:] VALIDSIG " in line
            }
            self.assertEqual({provenance["signingKeyFingerprint"]}, valid_signers)

    def test_canonical_sources_contain_no_retired_plugin_identifiers(self) -> None:
        retired = re.compile(r"cpp-standards|gpp-standards|windows-standards|agent-process:")
        files = [ROOT / ".agents" / "gen_skill_routes.py"]
        for scope in self.sources["scopes"]:
            files.extend((ROOT / scope["root"]).rglob("*.md"))
        offenders = [path.relative_to(ROOT).as_posix() for path in files if retired.search(path.read_text(encoding="utf-8"))]
        self.assertEqual([], offenders)

    def test_canonical_hooks_contain_no_retired_identifiers(self) -> None:
        retired = re.compile(r"cpp-standards|gpp-standards|windows-standards|agent-process:")
        hooks = [ROOT / ".agents" / "hooks" / "session_context.py", ROOT / "plugins" / "cpp" / "hooks" / "session_context.py"]
        self.assertEqual([], [path.relative_to(ROOT).as_posix() for path in hooks if retired.search(path.read_text(encoding="utf-8"))])

    def test_compatibility_skill_instructions_use_available_namespaces(self) -> None:
        identifier = re.compile(r"(?<![-/\w])([a-z0-9-]+):(?!:)([a-z][a-z0-9-]+)")
        directive = re.compile(r"(?i)\b(load|apply|follow|requires?|on top of|supplies)\b")
        inventories = {plugin: {path.parent.name for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")} for plugin in self.payloads["payloads"]}
        offenders = []
        for plugin in self.payloads["compatibilityAliases"]:
            available = {plugin, *self.payloads["dependencies"].get(plugin, [])}
            for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md"):
                for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if not directive.search(line):
                        continue
                    for namespace, skill in identifier.findall(line):
                        if namespace not in available or skill not in inventories.get(namespace, set()):
                            offenders.append(f"{path.relative_to(ROOT).as_posix()}:{line_number}: {namespace}:{skill}")
        self.assertEqual([], offenders)

    def test_compatibility_payload_skill_identifiers_resolve(self) -> None:
        identifier = re.compile(r"(?<![-/\w])([a-z0-9-]+):(?!:)([a-z][a-z0-9-]+)")
        inventories = {plugin: {path.parent.name for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")} for plugin in self.payloads["payloads"]}
        inventories.update({plugin: set(contract["skills"]) for plugin, contract in self.contract["legacyExternalPlugins"].items()})
        offenders = []
        for plugin in self.payloads["compatibilityAliases"]:
            package_root = ROOT / "plugins" / plugin
            for pattern in ("*.md", "*.py"):
                for path in package_root.rglob(pattern):
                    for namespace, skill in identifier.findall(path.read_text(encoding="utf-8")):
                        if namespace not in inventories or skill not in inventories[namespace]:
                            offenders.append(f"{path.relative_to(ROOT).as_posix()}: {namespace}:{skill}")
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
