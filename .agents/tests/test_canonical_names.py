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

    def test_only_current_packages_and_skill_names_are_published(self) -> None:
        canonical = {
            "cpp": {"build", "style", "structure", "testing", "libraries", "direction", "knowledge", "learning", "domain-design", "mixins"},
            "gpp": {"toolchain", "scaffold"}, "msvc": {"toolchain", "scaffold"},
            "win32": {"style", "knowledge", "overview", "scaffold"},
        }
        self.assertEqual(set(canonical), set(self.sources["packages"]))
        self.assertEqual(set(canonical), set(self.payloads["payloads"]))
        for scope in self.sources["scopes"]:
            plugin = scope["plugin"]
            authored = {path.parent.name for path in (ROOT / scope["root"]).glob("*/*/SKILL.md")}
            packaged = {path.parent.name for path in (ROOT / "plugins" / plugin / "skills").glob("*/SKILL.md")}
            self.assertEqual(canonical[plugin], authored)
            self.assertEqual(authored, packaged)
            selection = read_json(ROOT / "plugins" / plugin / "selection.json")
            self.assertNotIn("compatibilitySkillAliases", selection)
        self.assertEqual(set(canonical), {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()})


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
            ("msvc", "scaffold", "msvc", "New-MsvcProject.ps1"),
            ("win32", "scaffold", "win32", "Add-Win32App.ps1"),
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



if __name__ == "__main__":
    unittest.main()
