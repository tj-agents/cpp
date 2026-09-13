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
GENERATOR = ROOT / ".agents" / "gen_skill_routes.py"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
        cls.generator = load_generator()

    def test_public_plugins_are_the_three_layers_in_order(self) -> None:
        self.assertEqual(["base", "windows", "gcc"], self.payloads["publicPlugins"])
        names = [plugin["name"] for plugin in self.marketplace["plugins"]]
        self.assertEqual(self.payloads["publicPlugins"], names[:3])

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
        self.assertEqual({"cpp-standards", "gpp-standards"}, set(aliases))
        for name, alias in aliases.items():
            self.assertNotIn(name, public)
            self.assertIn(alias["replacedBy"], public)
            self.assertGreaterEqual(date.fromisoformat(alias["removeAfter"]), date.today())

    def test_generated_routes_reference_real_skill_contracts(self) -> None:
        local_skills = {
            path.parent.name
            for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")
        }
        public_domains = {
            plugin: set(self.payloads["payloads"][plugin])
            for plugin in self.payloads["publicPlugins"]
        }
        skill_domains = {}
        for skill_file in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            text = skill_file.read_text(encoding="utf-8")
            match = re.search(r"`standards/([^/]+)/", text)
            self.assertIsNotNone(match, skill_file)
            skill_domains[skill_file.parent.name] = match.group(1)

        external = self.contract["externalPlugins"]
        for kind in self.generator.CANONICAL_KINDS:
            for route in self.generator.routes(kind)["routes"]:
                for identifier in route.get("skills", []):
                    plugin, skill = identifier.split(":", 1)
                    if plugin in public_domains:
                        self.assertIn(skill, local_skills, identifier)
                        self.assertIn(skill_domains[skill], public_domains[plugin], identifier)
                    else:
                        self.assertIn(plugin, external, identifier)
                        self.assertIn(skill, external[plugin]["skills"], identifier)

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

        manifest_bytes = (evidence_root / "plugin.json").read_bytes()
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

        commit_bytes = (evidence_root / "commit.txt").read_bytes()
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
            subprocess.run(
                ["git", "verify-commit", contract["sourceCommit"]],
                capture_output=True,
                cwd=repository,
                env=environment,
                check=True,
            )

    def test_canonical_sources_contain_no_retired_plugin_identifiers(self) -> None:
        retired = re.compile(r"cpp-standards|gpp-standards|windows-standards|agent-process:")
        roots = [ROOT / "standards", ROOT / ".agents" / "skills"]
        files = [ROOT / ".agents" / "gen_skill_routes.py"]
        for source_root in roots:
            files.extend(source_root.rglob("*.md"))
        offenders = []
        for path in files:
            if retired.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], offenders)

    def test_canonical_hooks_contain_no_retired_identifiers(self) -> None:
        retired = re.compile(r"cpp-standards|gpp-standards|windows-standards|agent-process:")
        hooks = [
            ROOT / ".agents" / "hooks" / "session_context.py",
            ROOT / "plugins" / "base" / "hooks" / "session_context.py",
        ]
        self.assertEqual(
            [],
            [path.relative_to(ROOT).as_posix() for path in hooks if retired.search(path.read_text(encoding="utf-8"))],
        )

    def test_compatibility_payload_skill_identifiers_resolve(self) -> None:
        identifier = re.compile(r"(?<![-\w])([a-z0-9-]+):([a-z0-9-]+)")
        inventories = {
            plugin: {
                path.parent.name
                for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")
            }
            for plugin in self.payloads["compatibilityAliases"]
        }
        inventories.update(
            {
                plugin: set(contract["skills"])
                for plugin, contract in self.contract["legacyExternalPlugins"].items()
            }
        )
        offenders = []
        for plugin in self.payloads["compatibilityAliases"]:
            root = ROOT / "plugins" / plugin
            for pattern in ("*.md", "*.py"):
                for path in root.rglob(pattern):
                    for namespace, skill in identifier.findall(path.read_text(encoding="utf-8")):
                        if namespace not in inventories or skill not in inventories[namespace]:
                            offenders.append(
                                f"{path.relative_to(ROOT).as_posix()}: {namespace}:{skill}"
                            )
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
