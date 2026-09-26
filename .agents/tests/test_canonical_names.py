import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAYLOADS = ROOT / ".agents" / "plugins" / "payloads.json"
SOURCES = ROOT / ".agents" / "plugins" / "sources.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CanonicalNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payloads = read_json(PAYLOADS)
        cls.sources = read_json(SOURCES)

    def test_short_canonical_names_and_published_legacy_identifiers_coexist(self) -> None:
        canonical = {
            "cpp": {"build", "style", "structure", "testing", "libraries", "direction", "knowledge", "learning", "domain-design", "mixins"},
            "gpp": {"toolchain", "scaffold"},
            "msvc": {"toolchain", "scaffold"},
            "win32": {"style", "knowledge", "overview", "scaffold"},
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
            "base": legacy["cpp"] | {"domain-design", "mixins"},
            "cpp-standards": legacy["cpp"] | {"domain-design", "mixins"},
            "gcc": {"gcc-toolchain", "gpp-scaffold"},
            "gpp-standards": legacy["gpp"],
            "windows": legacy["msvc"] | legacy["win32"] | {"win32-scaffold"},
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
        cases = [
            ("gpp", "scaffold", "gpp", "new-gpp-project.sh"),
            ("gcc", "gpp-scaffold", "gpp", "new-gpp-project.sh"),
            ("gpp-standards", "gpp-scaffold", "gpp", "new-gpp-project.sh"),
            ("msvc", "scaffold", "msvc", "New-MsvcProject.ps1"),
            ("windows", "msvc-scaffold", "msvc", "New-MsvcProject.ps1"),
            ("win32", "scaffold", "win32", "Add-Win32App.ps1"),
            ("windows", "win32-scaffold", "win32", "Add-Win32App.ps1"),
        ]
        for plugin, name, scope, script in cases:
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

    def test_every_host_manifest_names_the_canonical_repository(self) -> None:
        manifests = sorted(
            ROOT / ".agents" / "plugins" / "manifests" / host / f"{package}.json"
            for host in ("claude", "codex")
            for package in self.payloads["payloads"]
        )
        self.assertEqual(2 * len(self.payloads["payloads"]), len(manifests))
        for manifest in manifests:
            self.assertEqual("https://github.com/tj-agents/cpp", read_json(manifest)["repository"], manifest.name)

    def test_no_generated_or_authored_file_is_git_ignored(self) -> None:
        # An ignored template is present locally but missing from every clone and package.
        if shutil.which("git") is None or not (ROOT / ".git").exists():
            self.skipTest("not a git checkout")
        files = [
            path.relative_to(ROOT).as_posix()
            for top in (".agents", ".claude", ".codex", "plugins")
            for path in (ROOT / top).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ]
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            cwd=ROOT, input="\n".join(files), capture_output=True, text=True,
        )
        self.assertEqual("", ignored.stdout)

    def test_compatibility_packages_never_name_canonical_identifiers(self) -> None:
        canonical = re.compile(r"(?<![\w@-])(?:cpp|gpp|msvc|win32):[a-z][a-z0-9-]*")
        compatibility = set(self.payloads["payloads"]) - set(self.payloads["publicPlugins"])
        self.assertEqual({"base", "gcc", "windows", "cpp-standards", "gpp-standards"}, compatibility)
        for plugin in sorted(compatibility):
            for path in sorted((ROOT / "plugins" / plugin).rglob("*")):
                if not path.is_file() or path.suffix not in {".md", ".json", ".py", ".sh", ".ps1", ".in"}:
                    continue
                leaked = canonical.findall(path.read_text(encoding="utf-8"))
                self.assertEqual([], leaked, path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    unittest.main()
